"""Apply the "own-screen view" change (all layouts) to the private emulator source copy (emulator-src/pcsx2).

Start from the source as it is in the original project (digimon-online state); in the working copy that is
    git -C emulator-src/pcsx2 checkout -- pcsx2      (the PS2Net changes are staged there, so they stay)
    and delete pcsx2/GS/GSPresentView.h if it exists
then
    python -I tools/lane-v3/apply_ownview_patch.py <path to emulator-src/pcsx2>

Display only. When a PS2Net session runs and the game has a settings file next to its patch file
(<patches folder>/<SERIAL>_<CRC>.view), each PC shows its own player's view of the game picture:
  layout 1  one picture with one part per player      -> show this player's part, stretched to the normal area
  layout 2  full-size views drawn one after the other -> the PC of the first view shows a copy taken at a marker
            (a LABEL register write in the draw list); the other PC shows the final picture   [hardware renderer]
  layout 3  the players' pictures on alternating video frames -> show only this player's frames, hold in between
Nothing in the emulated PS2 changes. Test snapshots stay the unchanged picture unless SnapView = 1.
Also adds the test-only session key DumpFrames (main memory written to a file at exact session frames).
Files are CRLF and stay CRLF. Every anchor is checked; the script refuses to run on already patched files.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(sys.argv[1])


def edit(rel, steps, append=""):
    path = ROOT / rel
    text = path.read_bytes().decode("utf-8").replace("\r\n", "\n")
    if "GSPresentView" in text or "OnFramePush" in text:
        sys.exit(f"{rel}: already patched")
    for old, new in steps:
        n = text.count(old)
        if n != 1:
            sys.exit(f"{rel}: anchor found {n} times (expected 1):\n{old[:200]}")
        text = text.replace(old, new, 1)
    text += append
    path.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))
    print("patched", rel)


# ---------------------------------------------------------------------------------------------------------------
HEADER = r'''// SPDX-License-Identifier: GPL-3.0+
// PS2Net own-screen view: what THIS PC shows of the game's picture. Not part of upstream PCSX2.
// Used when a game (with a patch) draws one view per player: each PC then shows only its own player's view.
// Display only: nothing in the emulated machine changes, so it cannot affect the sync between the PCs.

#pragma once

#include "common/Pcsx2Types.h"

class GSTexture;

namespace GSPresentView
{
	struct State
	{
		// 0 the whole picture; 1 a part of the picture; 2 the copy taken at a marker; 3 alternate video frames
		u8 kind = 0;
		// kind 1: the part, as fractions (0..1) of the game picture; it is stretched over the normal display area
		float left = 0.0f, top = 0.0f, right = 1.0f, bottom = 1.0f;
		// The next two are set whenever the game has a full-size layout, also while another layout is shown,
		// because a marker can arrive before the layout it belongs to is known here.
		// kind 2: this PC shows the copy taken at the marker instead of the final picture
		bool show_copy = false;
		// kind 2: low 32 bits of the LABEL register write (GS register 0x62) that marks the moment
		u32 marker_id = 0;
		// kind 2: at the marker, copy the frame buffer that is on display instead of the one being drawn to
		bool marker_shown_buffer = false;
		// kind 2: the copy is shown for at most this many video frames after its marker (0 = until the next one)
		u32 marker_hold = 8;
		// kind 2, tests only: act as if a marker for the frame buffer on display came after this many draws of a
		// video frame
		u32 fake_after_draws = 0;
		// kind 2, tests only: the test marker comes only in every Nth video frame
		u32 fake_every = 1;
		// kind 3: the picture of the video frame pushed next belongs to this PC's player (or to everybody)
		bool mine = true;
		// screenshots show what this PC shows instead of the unchanged picture
		bool in_screenshots = false;
	};

	// GS thread only: post it with MTGS::RunOnGSThread BEFORE the video frame it applies to is pushed.
	void Apply(const State& state);
	// GS thread only: the next picture is merged and shown unchanged (for a test snapshot of the real picture).
	void FullPictureOnce();

	// ---- used inside the GS code (GS thread) ----
	bool NoDeinterlace(); // kind 3: consecutive video frames must not be mixed
	bool MarkerWanted(u32 label_id);
	// test: counts one draw; true once per video frame when the test threshold is reached
	bool FakeMarkerDue(u32 frame_block);
	bool MarkerOfShownBuffer();
	bool ShownFrameBuffer(u32* bp, u32* psm); // kind 2: the frame buffer that was shown last
	extern bool g_count_draws;
	void OnLabel(u32 label_id); // a LABEL register write arrived in the draw stream
	void OnDraw(); // one draw was done (only does something in the marker test)
	void StoreMarkerCopy(u32 bp, GSTexture* tex);
	GSTexture* MarkerCopyFor(u32 bp, u32 psm, GSTexture* tex); // nullptr = show tex itself
} // namespace GSPresentView
'''

# ---------------------------------------------------------------------------------------------------------------
GS_BLOCK = r'''static GSVector4 s_last_draw_rect;

// ---------------------------------------------------------------------------------------------------------------
// PS2Net own-screen view (display only), see GS/GSPresentView.h. Everything here runs on the GS thread.
struct ViewMarkerCopy
{
	u32 bp = 0;
	GSTexture* tex = nullptr;
	u64 at = 0; // video frame count when it was taken
};
static GSPresentView::State s_view;
static GSTexture* s_view_hold = nullptr; // kind 3: copy of the last picture that belonged to this PC
static std::array<ViewMarkerCopy, 4> s_view_marker; // kind 2: copies taken at the marker, one per frame buffer
static u32 s_view_marker_next = 0;
static u32 s_view_full_once = 0; // video frames for which the unchanged picture is merged (test snapshots)
static u64 s_view_draws = 0; // kind 2 test: draws since the last vsync
static u64 s_view_draws_max = 0;
static u32 s_view_log_target = 0;
static u64 s_view_vsyncs = 0; // video frames presented, for the age of a marker copy
static u32 s_view_shown_bp = 0xFFFFFFFFu, s_view_shown_psm = 0; // kind 2: the frame buffer shown last
static bool s_view_fake_done = false;
static u32 s_view_log_store = 0, s_view_log_hit = 0, s_view_log_miss = 0, s_view_log_draws = 0; // a few log lines only
bool GSPresentView::g_count_draws = false;

static void ReleaseViewHold()
{
	if (s_view_hold && g_gs_device)
		g_gs_device->Recycle(s_view_hold);
	s_view_hold = nullptr;
}

static void ReleaseViewMarkers()
{
	for (ViewMarkerCopy& m : s_view_marker)
	{
		if (m.tex && g_gs_device)
			g_gs_device->Recycle(m.tex);
		m = ViewMarkerCopy();
	}
}

void GSPresentView::Apply(const State& state)
{
	if (state.kind != 3)
		ReleaseViewHold();
	// Copies taken at a marker are dropped when the full-size layout ends or this PC does not show them.
	if ((s_view.kind == 2 && state.kind != 2) || !state.show_copy || state.marker_id == 0)
		ReleaseViewMarkers();
	if (state.marker_id == 0)
		s_view_shown_bp = 0xFFFFFFFFu;
	s_view = state;
	if (s_view.kind == 1 && !(s_view.right > s_view.left && s_view.bottom > s_view.top))
		s_view.kind = 0;
	g_count_draws = (s_view.kind == 2 && s_view.fake_after_draws != 0);
}

void GSPresentView::FullPictureOnce()
{
	s_view_full_once = 2;
}

bool GSPresentView::NoDeinterlace()
{
	return s_view.kind == 3;
}

bool GSPresentView::MarkerWanted(u32 label_id)
{
	return s_view.marker_id != 0 && label_id == s_view.marker_id;
}

bool GSPresentView::MarkerOfShownBuffer()
{
	return s_view.marker_shown_buffer;
}

bool GSPresentView::ShownFrameBuffer(u32* bp, u32* psm)
{
	if (s_view_shown_bp == 0xFFFFFFFFu)
		return false;
	*bp = s_view_shown_bp;
	*psm = s_view_shown_psm;
	return true;
}

bool GSPresentView::FakeMarkerDue(u32 frame_block)
{
	if (s_view.kind != 2 || !s_view.fake_after_draws)
		return false;
	s_view_draws++;
	if (frame_block == s_view_shown_bp && (s_view_log_target++ % 900) < 3 && s_view_log_target < 20000)
	{
		Console.WriteLn("(PS2Net view) marker test: draw %llu of this video frame goes to the frame buffer on display (%05x)",
			static_cast<unsigned long long>(s_view_draws), frame_block);
	}
	if (s_view_draws < s_view.fake_after_draws || s_view_fake_done)
		return false;
	if (s_view.fake_every > 1 && (s_view_vsyncs % s_view.fake_every) != 0)
		return false;
	s_view_fake_done = true;
	return true;
}

void GSPresentView::StoreMarkerCopy(u32 bp, GSTexture* tex)
{
	// Only the PC that shows the copy needs it.
	if (!s_view.show_copy || !tex || !g_gs_device)
		return;
	ViewMarkerCopy* slot = nullptr;
	for (ViewMarkerCopy& m : s_view_marker)
	{
		if (m.tex && m.bp == bp)
			slot = &m;
	}
	if (!slot)
	{
		slot = &s_view_marker[s_view_marker_next];
		s_view_marker_next = (s_view_marker_next + 1) % static_cast<u32>(s_view_marker.size());
	}
	const GSVector2i size = tex->GetSize();
	if (slot->tex && (slot->tex->GetWidth() != size.x || slot->tex->GetHeight() != size.y || slot->tex->GetFormat() != tex->GetFormat()))
	{
		g_gs_device->Recycle(slot->tex);
		slot->tex = nullptr;
	}
	if (!slot->tex)
		slot->tex = g_gs_device->CreateRenderTarget(size.x, size.y, tex->GetFormat(), false);
	if (!slot->tex)
		return;
	slot->bp = bp;
	slot->at = s_view_vsyncs;
	g_gs_device->CopyRect(tex, slot->tex, GSVector4i(0, 0, size.x, size.y), 0, 0);
	if (s_view_log_store < 12)
	{
		s_view_log_store++;
		Console.WriteLn("(PS2Net view) marker: copied frame buffer %05x (%dx%d) after %llu draws of this video frame", bp, size.x, size.y,
			static_cast<unsigned long long>(s_view_draws));
	}
}

GSTexture* GSPresentView::MarkerCopyFor(u32 bp, u32 psm, GSTexture* tex)
{
	if (s_view.marker_id == 0 || !tex)
		return nullptr;
	s_view_shown_bp = bp;
	s_view_shown_psm = psm;
	if (s_view.kind != 2 || !s_view.show_copy || s_view_full_once)
		return nullptr;
	for (const ViewMarkerCopy& m : s_view_marker)
	{
		if (m.tex && m.bp == bp && m.tex->GetWidth() == tex->GetWidth() && m.tex->GetHeight() == tex->GetHeight() &&
			(!s_view.marker_hold || s_view_vsyncs - m.at <= s_view.marker_hold))
		{
			if (s_view_log_hit < 4)
			{
				s_view_log_hit++;
				Console.WriteLn("(PS2Net view) marker: showing the copy of frame buffer %05x", bp);
			}
			return m.tex;
		}
	}
	if ((s_view_log_miss++ % 900) < 2 && s_view_log_miss < 20000)
	{
		Console.WriteLn("(PS2Net view) marker: no copy for the displayed frame buffer %05x (%dx%d); copies held: %05x %05x %05x %05x", bp,
			tex->GetWidth(), tex->GetHeight(), s_view_marker[0].tex ? s_view_marker[0].bp : 0xFFFFF, s_view_marker[1].tex ? s_view_marker[1].bp : 0xFFFFF,
			s_view_marker[2].tex ? s_view_marker[2].bp : 0xFFFFF, s_view_marker[3].tex ? s_view_marker[3].bp : 0xFFFFF);
	}
	return nullptr;
}

// kind 3: the picture this PC shows for the video frame. The newest one if it is ours (a copy is kept when
// new_frame is true), otherwise the kept copy of our last one.
static GSTexture* PickPresentPicture(GSTexture* current, bool new_frame)
{
	if (s_view.kind != 3 || !current)
		return current;
	if (s_view.mine)
	{
		if (new_frame)
		{
			const GSVector2i size = current->GetSize();
			if (s_view_hold && (s_view_hold->GetWidth() != size.x || s_view_hold->GetHeight() != size.y))
				ReleaseViewHold();
			if (!s_view_hold)
				s_view_hold = g_gs_device->CreateRenderTarget(size.x, size.y, GSTexture::Format::Color, false);
			if (s_view_hold)
				g_gs_device->StretchRect(current, s_view_hold, GSVector4(0.0f, 0.0f, static_cast<float>(size.x), static_cast<float>(size.y)),
					ShaderConvert::COPY, Nearest);
		}
		return current;
	}
	return s_view_hold ? s_view_hold : current;
}

// kind 1: narrows the source rectangle to this PC's part. Call it AFTER the destination rectangle was computed
// from the whole picture, so the part is stretched over the same screen area the whole picture would cover.
static void ApplyPresentView(GSVector4i& src_rect, GSVector4& src_uv, const GSVector2i& tex_size)
{
	if (s_view.kind != 1)
		return;
	const float w = static_cast<float>(src_rect.z - src_rect.x);
	const float h = static_cast<float>(src_rect.w - src_rect.y);
	float l = static_cast<float>(src_rect.x) + w * s_view.left;
	float t = static_cast<float>(src_rect.y) + h * s_view.top;
	float r = static_cast<float>(src_rect.x) + w * s_view.right;
	float b = static_cast<float>(src_rect.y) + h * s_view.bottom;
	// Stay half a texel away from an inner edge, so filtering does not pull in the neighbouring part.
	if (s_view.left > 0.0f)
		l += 0.5f;
	if (s_view.top > 0.0f)
		t += 0.5f;
	if (s_view.right < 1.0f)
		r -= 0.5f;
	if (s_view.bottom < 1.0f)
		b -= 0.5f;
	src_uv = GSVector4(l, t, r, b) / GSVector4(tex_size).xyxy();
	src_rect = GSVector4i(static_cast<int>(l), static_cast<int>(t), static_cast<int>(std::ceil(r)), static_cast<int>(std::ceil(b)));
}

static void ViewEndOfVSync()
{
	if (s_view_full_once)
		s_view_full_once--;
	if (GSPresentView::g_count_draws && s_view_draws > s_view_draws_max && s_view_log_draws < 40)
	{
		s_view_log_draws++;
		s_view_draws_max = s_view_draws;
		Console.WriteLn("(PS2Net view) marker test: %llu draws in one video frame (highest so far)", static_cast<unsigned long long>(s_view_draws));
	}
	s_view_draws = 0;
	s_view_fake_done = false;
	s_view_vsyncs++;
}
// ---------------------------------------------------------------------------------------------------------------
'''

gs_steps = [
    ('#include "GS/GSPerfMon.h"\n', '#include "GS/GSPerfMon.h"\n#include "GS/GSPresentView.h"\n'),
    ('#include <array>\n#include <deque>\n', '#include <array>\n#include <cmath>\n#include <deque>\n'),
    ('#include "common/FileSystem.h"\n#include "common/Image.h"\n',
     '#include "common/Console.h"\n#include "common/FileSystem.h"\n#include "common/Image.h"\n'),
    ("static GSVector4 s_last_draw_rect;\n", GS_BLOCK),
    ("void GSRenderer::Destroy()\n{\n\tGSCapture::EndCapture();\n",
     "void GSRenderer::Destroy()\n{\n\tGSCapture::EndCapture();\n\tReleaseViewHold();\n\tReleaseViewMarkers();\n"),
    # Merge: no deinterlacing across video frames when the players' pictures alternate
    ("!GSConfig.DisableInterlaceOffset && GSConfig.InterlaceMode != GSInterlaceMode::Off)",
     "!GSConfig.DisableInterlaceOffset && GSConfig.InterlaceMode != GSInterlaceMode::Off && !GSPresentView::NoDeinterlace())"),
    ("\tif ((tex[0] || tex[1]) && isReallyInterlaced() && GSConfig.InterlaceMode != GSInterlaceMode::Off)\n",
     "\tif ((tex[0] || tex[1]) && isReallyInterlaced() && GSConfig.InterlaceMode != GSInterlaceMode::Off && !GSPresentView::NoDeinterlace())\n"),
    # VSync
    ("\tconst bool blank_frame = !Merge(field);\n",
     "\tconst bool blank_frame = !Merge(field);\n\n"
     "\t// PS2Net own-screen view, alternate video frames: this PC's own picture is always shown, even when the\n"
     "\t// emulator would skip it as a repeated frame, and a copy of it is kept for the other player's frames.\n"
     "\tif (s_view.kind == 3 && s_view.mine)\n"
     "\t{\n"
     "\t\tskip_frame = false;\n"
     "\t\tif (!blank_frame)\n"
     "\t\t\tPickPresentPicture(g_gs_device->GetCurrent(), true);\n"
     "\t}\n"),
    ("\t\tGSTexture* current = g_gs_device->GetCurrent();\n\t\tif (current && !blank_frame)\n\t\t{\n",
     "\t\tGSTexture* current = g_gs_device->GetCurrent();\n\t\tif (current && !blank_frame)\n\t\t{\n"
     "\t\t\tcurrent = PickPresentPicture(current, false);\n"),
    ("\t\t\ts_last_draw_rect = draw_rect;\n\n\t\t\tif (GSConfig.CASMode != GSCASMode::Disabled)",
     "\t\t\ts_last_draw_rect = draw_rect;\n\t\t\tApplyPresentView(src_rect, src_uv, current->GetSize());\n\n"
     "\t\t\tif (GSConfig.CASMode != GSCASMode::Disabled)"),
    ("\tif (GSConfig.ShouldDump(s_n, g_perfmon.GetFrame()) && GSConfig.SaveTransferImages)\n\t\tDumpTransferImages();\n}\n",
     "\tViewEndOfVSync();\n\n"
     "\tif (GSConfig.ShouldDump(s_n, g_perfmon.GetFrame()) && GSConfig.SaveTransferImages)\n\t\tDumpTransferImages();\n}\n"),
    # PresentCurrentFrame
    ("\t\tGSTexture* current = g_gs_device->GetCurrent();\n\t\tif (current)\n\t\t{\n"
     "\t\t\tconst GSVector4i src_rect(CalculateDrawSrcRect(current, m_real_size));\n"
     "\t\t\tconst GSVector4 src_uv(GSVector4(src_rect) / GSVector4(current->GetSize()).xyxy());\n"
     "\t\t\tconst GSVector4 draw_rect(CalculateDrawDstRect(g_gs_device->GetWindowWidth(), g_gs_device->GetWindowHeight(),\n"
     "\t\t\t\tsrc_rect, current->GetSize(), s_display_alignment, g_gs_device->UsesLowerLeftOrigin(),\n"
     "\t\t\t\tGetVideoMode() == GSVideoMode::SDTV_480P));\n"
     "\t\t\ts_last_draw_rect = draw_rect;\n",
     "\t\tGSTexture* current = PickPresentPicture(g_gs_device->GetCurrent(), false);\n\t\tif (current)\n\t\t{\n"
     "\t\t\tGSVector4i src_rect(CalculateDrawSrcRect(current, m_real_size));\n"
     "\t\t\tGSVector4 src_uv(GSVector4(src_rect) / GSVector4(current->GetSize()).xyxy());\n"
     "\t\t\tconst GSVector4 draw_rect(CalculateDrawDstRect(g_gs_device->GetWindowWidth(), g_gs_device->GetWindowHeight(),\n"
     "\t\t\t\tsrc_rect, current->GetSize(), s_display_alignment, g_gs_device->UsesLowerLeftOrigin(),\n"
     "\t\t\t\tGetVideoMode() == GSVideoMode::SDTV_480P));\n"
     "\t\t\ts_last_draw_rect = draw_rect;\n"
     "\t\t\tApplyPresentView(src_rect, src_uv, current->GetSize());\n"),
    # SaveSnapshotToMemory
    ("\tGSTexture* const current = g_gs_device->GetCurrent();\n\tif (!current)\n\t{\n\t\t*width = 0;\n",
     "\t// PS2Net own-screen view: screenshots keep the unchanged picture unless the session asked for this PC's view.\n"
     "\tGSTexture* const current = s_view.in_screenshots ? PickPresentPicture(g_gs_device->GetCurrent(), false) : g_gs_device->GetCurrent();\n"
     "\tif (!current)\n\t{\n\t\t*width = 0;\n"),
    ("\tconst GSVector4i src_rect(CalculateDrawSrcRect(current, m_real_size));\n"
     "\tconst GSVector4 src_uv(GSVector4(src_rect) / GSVector4(current->GetSize()).xyxy());\n\n"
     "\tconst bool is_progressive = (GetVideoMode() == GSVideoMode::SDTV_480P);\n",
     "\tGSVector4i src_rect(CalculateDrawSrcRect(current, m_real_size));\n"
     "\tGSVector4 src_uv(GSVector4(src_rect) / GSVector4(current->GetSize()).xyxy());\n\n"
     "\tconst bool is_progressive = (GetVideoMode() == GSVideoMode::SDTV_480P);\n"),
    ("\tconst u32 draw_width = static_cast<u32>(draw_rect.z - draw_rect.x);\n",
     "\tif (s_view.in_screenshots)\n"
     "\t\tApplyPresentView(src_rect, src_uv, current->GetSize());\n"
     "\tconst u32 draw_width = static_cast<u32>(draw_rect.z - draw_rect.x);\n"),
]

# ---------------------------------------------------------------------------------------------------------------
HW_H_STEPS = [
    ("\t__fi static GSRendererHW* GetInstance() { return static_cast<GSRendererHW*>(g_gs_renderer.get()); }\n",
     "\t__fi static GSRendererHW* GetInstance() { return static_cast<GSRendererHW*>(g_gs_renderer.get()); }\n"
     "\t// PS2Net own-screen view (GS/GSPresentView.h): keep a copy of the frame buffer being drawn, as it is now.\n"
     "\tvoid CaptureViewMarker(bool flush_first, bool shown_buffer);\n"),
]

HW_CPP_STEPS = [
    ('#include "GS/GSPerfMon.h"\n', '#include "GS/GSPerfMon.h"\n#include "GS/GSPresentView.h"\n'),
    ("\t\tt = rt->m_texture;\n\t\tscale = rt->m_scale;\n\n\t\tconst int delta = bp_adj - rt->m_TEX0.TBP0;",
     "\t\tt = rt->m_texture;\n\t\tscale = rt->m_scale;\n"
     "\t\t// PS2Net own-screen view: this PC may show the copy taken at the marker instead of the final picture.\n"
     "\t\tif (GSTexture* view_copy = GSPresentView::MarkerCopyFor(rt->m_TEX0.TBP0, rt->m_TEX0.PSM, t))\n"
     "\t\t\tt = view_copy;\n\n"
     "\t\tconst int delta = bp_adj - rt->m_TEX0.TBP0;"),
]

HW_CPP_APPEND = r'''
// ---------------------------------------------------------------------------------------------------------------
// PS2Net own-screen view (display only), see GS/GSPresentView.h.
void GSRendererHW::CaptureViewMarker(bool flush_first, bool shown_buffer)
{
	// Everything drawn so far must be in the frame buffer before it is copied.
	if (flush_first)
		Flush(GSFlushReason::UNKNOWN);
	// The frame buffer being drawn to, or (per-game setting, and in the test) the one that is on display.
	u32 bp = m_context->FRAME.Block();
	u32 psm = m_context->FRAME.PSM;
	if (shown_buffer && !GSPresentView::ShownFrameBuffer(&bp, &psm))
		return;
	GSTextureCache::Target* rt = g_texture_cache->GetTargetWithSharedBits(bp, psm);
	if (!rt || !rt->m_texture)
		return;
	rt->Update();
	GSPresentView::StoreMarkerCopy(rt->m_TEX0.TBP0, rt->m_texture);
}

void GSPresentView::OnLabel(u32 label_id)
{
	if (MarkerWanted(label_id) && GSIsHardwareRenderer())
		GSRendererHW::GetInstance()->CaptureViewMarker(true, MarkerOfShownBuffer());
}

void GSPresentView::OnDraw()
{
	if (!GSIsHardwareRenderer())
		return;
	GSRendererHW* const hw = GSRendererHW::GetInstance();
	if (FakeMarkerDue(hw->m_context->FRAME.Block()))
		hw->CaptureViewMarker(false, true);
}
'''

# ---------------------------------------------------------------------------------------------------------------
STATE_STEPS = [
    ('#include "GS/GSPerfMon.h"\n', '#include "GS/GSPerfMon.h"\n#include "GS/GSPresentView.h"\n'),
    ("\t(this->*m_fpGIFRegHandlers[r->A_D.ADDR & 0x7F])(&r->r);\n}\n",
     "\t// PS2Net own-screen view: a LABEL write can be the marker between two players' views (display only).\n"
     "\tif ((r->A_D.ADDR & 0x7F) == GIF_A_D_REG_LABEL)\n"
     "\t\tGSPresentView::OnLabel(r->r.U32[0]);\n"
     "\t(this->*m_fpGIFRegHandlers[r->A_D.ADDR & 0x7F])(&r->r);\n}\n"),
    ("\t\tif (!skip_draw)\n\t\t\tDraw();\n",
     "\t\tif (!skip_draw)\n\t\t\tDraw();\n\n"
     "\t\t// PS2Net own-screen view, marker test only.\n"
     "\t\tif (GSPresentView::g_count_draws)\n"
     "\t\t\tGSPresentView::OnDraw();\n"),
]

# ---------------------------------------------------------------------------------------------------------------
PS2NET_H_NEW = r'''	// Once per emulated frame, right BEFORE the finished picture is handed to the GS thread (Counters.cpp
	// VSyncStart). Own-screen view: tells the GS thread what this PC shows of the picture. Display only.
	void OnFramePush();

	// Called by the DualShock 2 poll handler. Returns false when the slot is not driven by the session.
'''

PS2NET_VIEW = r'''		// ------------------------------------------------------------------------------------------------------
		// Own-screen view (display only). Some games (with a patch) draw one view per player. A small settings
		// file next to the game's patch file, <patches folder>/<SERIAL>_<CRC>.view, tells how. The emulator holds
		// no game-specific numbers. Nothing here changes the emulated machine, so it cannot affect the sync.
		//   LayoutAddress = 000F6F00   EE address (hex) of the game's layout byte; 0 = none (TestLayout is used)
		//   SideValue = 1              layout value: ONE picture with one part per player (Player1.. below)
		//   MarkerValue = 2            layout value: full-size views drawn one after the other, a LABEL register
		//                              write (GS register 0x62) between them
		//   AlternateValue = 3         layout value: the players' pictures on alternating video frames
		//   Player1 = 0.5 0 1 1        side by side: left top right bottom, as fractions of the game picture
		//   Player2 = 0 0 0.5 1
		//   MarkerId = 56570001        marker layout: low 32 bits (hex) of the LABEL write
		//   MarkerPlayer = 1           marker layout: the player whose picture is complete at the marker
		//   MarkerBuffer = frame       marker layout: what is copied at the marker: frame = the frame buffer being
		//                              drawn to (FRAME register), display = the frame buffer that is on display
		//   MarkerHold = 8             marker layout: video frames a copy is shown without a new marker (0 = no limit)
		//   OwnerAddress = 000F6F02    alternate layout: EE address (hex) of a byte saying whose picture the
		//                              display registers select now (0 = player 1, 1 = player 2, other = all)
		//   LayoutDelay = 0            video frames (0..3) by which the game writes the layout and owner bytes before
		//                              the picture they describe is on display
		//   TestLayout / MarkerTestDraws / MarkerTestEvery   development and tests only
		struct ViewRect
		{
			float l = 0.0f, t = 0.0f, r = 1.0f, b = 1.0f;
			bool set = false;
		};
		struct ViewSettings
		{
			bool loaded = false;
			u32 layout_addr = 0;
			u32 side_value = 1;
			u32 marker_value = 2;
			u32 alternate_value = 3;
			u32 test_layout = 1;
			std::array<ViewRect, kMaxPlayers> rect;
			u32 marker_id = 0;
			u32 marker_player = 1;
			u32 marker_hold = 8;
			bool marker_shown_buffer = false;
			u32 marker_test_draws = 0;
			u32 marker_test_every = 1;
			u32 owner_addr = 0;
			u32 layout_delay = 0;
		};
		ViewSettings s_view;
		std::array<u8, 4> s_view_layout_hist{}; // the layout and owner bytes of the last video frames, newest first
		std::array<u8, 4> s_view_owner_hist{};
		GSPresentView::State s_view_posted;
		u32 s_view_repost = 0;

		void Log(const std::string& msg);

		void LoadViewSettings()
		{
			s_view = ViewSettings();
			s_view_layout_hist.fill(0);
			s_view_owner_hist.fill(0xFF);
			const std::string path = Path::Combine(EmuFolders::Patches,
				fmt::format("{}_{:08X}.view", VMManager::GetDiscSerial(), VMManager::GetDiscCRC()));
			const std::optional<std::string> text = FileSystem::ReadFileToString(path.c_str());
			if (!text)
				return;
			for (const std::string_view raw : StringUtil::SplitString(*text, '\n', true))
			{
				std::string_view line = StringUtil::StripWhitespace(raw);
				const size_t comment = line.find_first_of(";#");
				if (comment != std::string_view::npos)
					line = StringUtil::StripWhitespace(line.substr(0, comment));
				const size_t eq = line.find('=');
				if (line.empty() || eq == std::string_view::npos)
					continue;
				const std::string key = StringUtil::toLower(StringUtil::StripWhitespace(line.substr(0, eq)));
				std::string val(StringUtil::StripWhitespace(line.substr(eq + 1)));
				const u32 dec = StringUtil::FromChars<u32>(val).value_or(0);
				const u32 hex = StringUtil::FromChars<u32>(val, 16).value_or(0);
				if (key == "layoutaddress")
					s_view.layout_addr = hex;
				else if (key == "sidevalue" || key == "viewsvalue")
					s_view.side_value = dec;
				else if (key == "markervalue")
					s_view.marker_value = dec;
				else if (key == "alternatevalue")
					s_view.alternate_value = dec;
				else if (key == "testlayout")
					s_view.test_layout = dec;
				else if (key == "markerid")
					s_view.marker_id = hex;
				else if (key == "markerplayer")
					s_view.marker_player = dec;
				else if (key == "markerbuffer")
					s_view.marker_shown_buffer = (StringUtil::toLower(val) == "display");
				else if (key == "markerhold")
					s_view.marker_hold = dec;
				else if (key == "markertestevery")
					s_view.marker_test_every = dec;
				else if (key == "markertestdraws")
					s_view.marker_test_draws = dec;
				else if (key == "owneraddress")
					s_view.owner_addr = hex;
				else if (key == "layoutdelay")
					s_view.layout_delay = std::min<u32>(dec, 3);
				else if (key.size() == 7 && key.compare(0, 6, "player") == 0 && key[6] >= '1' && key[6] < static_cast<char>('1' + kMaxPlayers))
				{
					std::replace(val.begin(), val.end(), ',', ' ');
					std::vector<float> f;
					for (const std::string_view part : StringUtil::SplitString(val, ' ', true))
						if (const std::optional<float> n = StringUtil::FromChars<float>(part))
							f.push_back(*n);
					if (f.size() == 4 && f[2] > f[0] && f[3] > f[1] && f[0] >= 0.0f && f[1] >= 0.0f && f[2] <= 1.0f && f[3] <= 1.0f)
					{
						ViewRect& v = s_view.rect[key[6] - '1'];
						v.l = f[0];
						v.t = f[1];
						v.r = f[2];
						v.b = f[3];
						v.set = true;
					}
				}
			}
			s_view.loaded = true;
			std::string parts;
			for (u32 i = 0; i < kMaxPlayers; i++)
				if (s_view.rect[i].set)
					parts += fmt::format(" player {} = {} {} {} {};", i + 1, s_view.rect[i].l, s_view.rect[i].t, s_view.rect[i].r, s_view.rect[i].b);
			if (s_view.layout_delay)
				parts += fmt::format(" the bytes are {} video frame(s) ahead of the picture;", s_view.layout_delay);
			Log(fmt::format("view: settings file {} (layout byte at {:08X}; side by side = {}, marker = {} with id {:08X} for player {}, "
							"alternate = {} with owner byte at {:08X});{}",
				Path::GetFileName(path), s_view.layout_addr, s_view.side_value, s_view.marker_value, s_view.marker_id,
				s_view.marker_player, s_view.alternate_value, s_view.owner_addr, parts));
		}

		bool SameView(const GSPresentView::State& a, const GSPresentView::State& b)
		{
			return a.kind == b.kind && a.left == b.left && a.top == b.top && a.right == b.right && a.bottom == b.bottom &&
				   a.show_copy == b.show_copy && a.marker_id == b.marker_id && a.fake_after_draws == b.fake_after_draws &&
				   a.marker_hold == b.marker_hold && a.marker_shown_buffer == b.marker_shown_buffer && a.fake_every == b.fake_every &&
				   a.mine == b.mine && a.in_screenshots == b.in_screenshots;
		}

		void PostView(const GSPresentView::State& want, u32 frame, u32 who)
		{
			// Posted when something changes, and again now and then so a restarted GS thread gets it too.
			const bool same = SameView(want, s_view_posted);
			if (same && (want.kind == 0 || ++s_view_repost < 120))
				return;
			s_view_repost = 0;
			if (want.kind != s_view_posted.kind || want.show_copy != s_view_posted.show_copy)
			{
				static constexpr const char* names[] = {"whole picture", "this player's part of the picture",
					"full-size views with a marker", "alternate video frames"};
				std::string what = names[want.kind & 3];
				if (want.kind == 1 || want.kind == 3)
					what += fmt::format(", player {}", who + 1);
				if (want.kind == 2)
					what += want.show_copy ? ", this PC shows the copy taken at the marker" : ", this PC shows the final picture";
				if (want.kind != 0)
				{
					const u64 smode2 = *reinterpret_cast<const u64*>(PS2GS_BASE(0x12000020));
					what += fmt::format(" (video mode: interlaced {}, frame mode {})", smode2 & 1, (smode2 >> 1) & 1);
				}
				Log(fmt::format("view: {} from frame {}", what, frame));
			}
			s_view_posted = want;
			if (MTGS::IsOpen())
				MTGS::RunOnGSThread([want]() { GSPresentView::Apply(want); });
		}

		// ------------------------------------------------------------------------------------------------------
		// Log file (one per PC and session)
'''

PS2NET_ONFRAMEPUSH = r'''	void OnFramePush()
	{
		GSPresentView::State want;
		u32 who = 0, frame = 0;
		if (s_session && !s_session->ended && s_session->started && s_view.loaded && s_session->cfg.view != 0xFF)
		{
			const Session& s = *s_session;
			frame = s.frame;
			who = s.cfg.view ? (s.cfg.view - 1u) : s.me;
			// The bytes as the game has them now; what is on display may be the picture of LayoutDelay frames ago.
			for (u32 i = 3; i > 0; i--)
			{
				s_view_layout_hist[i] = s_view_layout_hist[i - 1];
				s_view_owner_hist[i] = s_view_owner_hist[i - 1];
			}
			s_view_layout_hist[0] = static_cast<u8>(s_view.layout_addr ? memRead8(s_view.layout_addr) : s_view.test_layout);
			s_view_owner_hist[0] = static_cast<u8>(s_view.owner_addr ? memRead8(s_view.owner_addr) : (s.frame & 1u));
			const u32 layout = s_view_layout_hist[s_view.layout_delay];
			want.in_screenshots = s.cfg.snap_view;
			// The marker of the full-size layout can arrive before its layout value is used here: always known.
			want.marker_id = s_view.marker_id;
			want.marker_hold = s_view.marker_hold;
			want.marker_shown_buffer = s_view.marker_shown_buffer;
			want.show_copy = (s_view.marker_id != 0 && who + 1 == s_view.marker_player);
			if (layout != 0 && layout == s_view.side_value)
			{
				if (who < kMaxPlayers && s_view.rect[who].set)
				{
					want.kind = 1;
					want.left = s_view.rect[who].l;
					want.top = s_view.rect[who].t;
					want.right = s_view.rect[who].r;
					want.bottom = s_view.rect[who].b;
				}
			}
			else if (layout != 0 && layout == s_view.marker_value)
			{
				want.kind = 2;
				want.fake_after_draws = s_view.marker_test_draws;
				want.fake_every = s_view.marker_test_every;
			}
			else if (layout != 0 && layout == s_view.alternate_value)
			{
				want.kind = 3;
				const u32 owner = s_view_owner_hist[s_view.layout_delay];
				want.mine = (owner == who) || owner >= kMaxPlayers;
			}
			if (want.kind == 0)
				want.in_screenshots = false;
		}
		PostView(want, frame, who);
	}

	void OnVsync()
	{
'''

ps2net_steps = [
    ('#include "GS/GS.h"\n', '#include "GS/GS.h"\n#include "GS/GSPresentView.h"\n#include "GS.h"\n'),
    ("\t\t\tstd::vector<u32> snap_frames;\n",
     "\t\t\tstd::vector<u32> snap_frames;\n"
     "\t\t\tstd::vector<u32> dump_frames; // test only: write the EE main memory to snap_dir at these frames\n"),
    ("\t\t\tu8 screen = 0; // 0 = 4:3 as the game was made, 1 = the game's widescreen 16:9 patch\n",
     "\t\t\tu8 screen = 0; // 0 = 4:3 as the game was made, 1 = the game's widescreen 16:9 patch\n"
     "\t\t\t// Own-screen view (display only): 0 = my own player's view, N = player N's view, 0xFF = whole picture.\n"
     "\t\t\tu8 view = 0;\n"
     "\t\t\tbool snap_view = false; // test snapshots show what this PC shows instead of the unchanged picture\n"),
    ('\t\t\t\telse if (key == "snapevery")\n',
     '\t\t\t\telse if (key == "dumpframes")\n'
     '\t\t\t\t\tc.dump_frames = ParseList(val);\n'
     '\t\t\t\telse if (key == "snapevery")\n'),
    ('\t\t\t\telse if (key == "peek")\n',
     '\t\t\t\telse if (key == "view")\n'
     '\t\t\t\t\tc.view = (StringUtil::toLower(val) == "off") ? 0xFF : static_cast<u8>(std::min<u32>(num, kMaxPlayers));\n'
     '\t\t\t\telse if (key == "snapview")\n'
     '\t\t\t\t\tc.snap_view = (num != 0);\n'
     '\t\t\t\telse if (key == "peek")\n'),
    ("\t\t// ------------------------------------------------------------------------------------------------------\n"
     "\t\t// Log file (one per PC and session)\n", PS2NET_VIEW),
    ("\t\t\t\tMTGS::RunOnGSThread([path]() { GSQueueSnapshot(path, 0); });\n",
     "\t\t\t\t// The snapshot is the unchanged picture unless SnapView asks for what this PC shows.\n"
     "\t\t\t\tconst bool full = !s.cfg.snap_view;\n"
     "\t\t\t\tMTGS::RunOnGSThread([path, full]() {\n"
     "\t\t\t\t\tif (full)\n"
     "\t\t\t\t\t\tGSPresentView::FullPictureOnce();\n"
     "\t\t\t\t\tGSQueueSnapshot(path, 0);\n"
     "\t\t\t\t});\n"),
    ("\t\t\tif (s.cfg.exit_at_frame && frame == s.cfg.exit_at_frame)\n",
     "\t\t\tif (!s.cfg.snap_dir.empty() &&\n"
     "\t\t\t\tstd::find(s.cfg.dump_frames.begin(), s.cfg.dump_frames.end(), frame) != s.cfg.dump_frames.end())\n"
     "\t\t\t{\n"
     "\t\t\t\t// Test only: the whole EE main memory at an exact session frame (read only).\n"
     '\t\t\t\tconst std::string dump_path = Path::Combine(s.cfg.snap_dir, fmt::format("p{}_ram_f{:06d}.bin", s.me + 1, frame));\n'
     '\t\t\t\tif (std::FILE* f = FileSystem::OpenCFile(dump_path.c_str(), "wb"))\n'
     "\t\t\t\t{\n"
     "\t\t\t\t\tstd::fwrite(eeMem->Main, 1, Ps2MemSize::MainRam, f);\n"
     "\t\t\t\t\tstd::fclose(f);\n"
     "\t\t\t\t}\n"
     "\t\t\t}\n"
     "\t\t\tif (s.cfg.exit_at_frame && frame == s.cfg.exit_at_frame)\n"),
    ("\t\t\tfor (PadInput& in : s->cur)\n\t\t\t\tin = NeutralInput();\n\t\t\ts_session = std::move(s);\n",
     "\t\t\tfor (PadInput& in : s->cur)\n\t\t\t\tin = NeutralInput();\n\t\t\ts_session = std::move(s);\n"
     "\t\t\tLoadViewSettings();\n"),
    ("\tvoid OnVsync()\n\t{\n", PS2NET_ONFRAMEPUSH),
    ("\tvoid OnVMShutdown()\n\t{\n\t\tEndSession(true);\n",
     "\tvoid OnVMShutdown()\n\t{\n\t\tEndSession(true);\n\t\tPostView(GSPresentView::State(), 0, 0);\n\t\ts_view = ViewSettings();\n"),
]

ps2net_h_steps = [
    ("\t// Called by the DualShock 2 poll handler. Returns false when the slot is not driven by the session.\n", PS2NET_H_NEW),
]

counters_steps = [
    ("\tif (!EmuConfig.GS.AdvancedFrameDisplay)\n\t{\n\t\tgsPostVsyncStart(); // MUST be after framelimit; doing so before causes funk with frame times!\n\t}\n",
     "\t// PS2Net own-screen view: choose what this PC shows of the picture, before the picture is pushed.\n"
     "\tPS2Net::OnFramePush();\n\n"
     "\tif (!EmuConfig.GS.AdvancedFrameDisplay)\n\t{\n\t\tgsPostVsyncStart(); // MUST be after framelimit; doing so before causes funk with frame times!\n\t}\n"),
]

hdr = ROOT / "pcsx2" / "GS" / "GSPresentView.h"
if hdr.exists():
    sys.exit("pcsx2/GS/GSPresentView.h already exists")

# the fast A+D path in GSState::Transfer needs its own indentation: patched with a regular expression
state_path = ROOT / "pcsx2" / "GS" / "GSState.cpp"
state_text = state_path.read_bytes().decode("utf-8").replace("\r\n", "\n")
fast = re.compile(r"^(\t+)\(this->\*m_fpGIFRegHandlers\[\(\(GIFPackedReg\*\)mem\)->A_D\.ADDR & 0x7F\]\)\(&\(\(GIFPackedReg\*\)mem\)->r\);\n", re.M)
if len(fast.findall(state_text)) != 1:
    sys.exit("GSState.cpp: fast A+D path not found exactly once")

edit("pcsx2/GS/Renderers/Common/GSRenderer.cpp", gs_steps)
edit("pcsx2/GS/Renderers/HW/GSRendererHW.h", HW_H_STEPS)
edit("pcsx2/GS/Renderers/HW/GSRendererHW.cpp", HW_CPP_STEPS, HW_CPP_APPEND)
edit("pcsx2/GS/GSState.cpp", STATE_STEPS)
# second pass on GSState.cpp for the fast path
state_text = state_path.read_bytes().decode("utf-8").replace("\r\n", "\n")
state_text = fast.sub(lambda m: (m.group(1) + "if ((((GIFPackedReg*)mem)->A_D.ADDR & 0x7F) == GIF_A_D_REG_LABEL)\n"
                                 + m.group(1) + "\tGSPresentView::OnLabel(((GIFPackedReg*)mem)->r.U32[0]);\n" + m.group(0)), state_text, count=1)
state_path.write_bytes(state_text.replace("\n", "\r\n").encode("utf-8"))
edit("pcsx2/PS2Net/PS2Net.h", ps2net_h_steps)
edit("pcsx2/PS2Net/PS2Net.cpp", ps2net_steps)
edit("pcsx2/Counters.cpp", counters_steps)
hdr.write_bytes(HEADER.replace("\n", "\r\n").encode("utf-8"))
print("created pcsx2/GS/GSPresentView.h")
