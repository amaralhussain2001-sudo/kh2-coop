"""One-off: add the "keep and paste" feature to the own-view emulator source (emulator-src/pcsx2).

  python -I tools/own/emu_keep_edit.py

Display only. A game patch that draws one view per player sends player 1's finished 3D picture through main memory
and back (the game's own capture and loader). With a raised picture quality it comes back at the PS2's own
sharpness. With this change the emulator keeps a copy of the picture at its own resolution when the game marks
the moment (a LABEL register write, "keep" id), and puts the copy into the frame buffer the game reloads it to
(second LABEL write, "restore" id). Nothing in the emulated machine changes.
The change is recorded afterwards in emulator-src/patches/ownview.patch (git diff of the source tree).
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent / "emulator-src" / "pcsx2"


def edit(rel, pairs):
    p = ROOT / rel
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    t = raw.decode("utf-8").replace("\r\n", "\n")
    for old, new in pairs:
        if t.count(old) != 1:
            raise SystemExit("%s: expected one place for %r (found %d)" % (rel, old[:60], t.count(old)))
        t = t.replace(old, new)
    p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
    print("edited", rel)


# ---- texture cache: keep a copy of a frame buffer, paste it into another one
edit("pcsx2/GS/Renderers/HW/GSTextureCache.h", [(
    """	Target* GetTargetWithSharedBits(u32 BP, u32 PSM) const;
""",
    """	Target* GetTargetWithSharedBits(u32 BP, u32 PSM) const;

	// PS2Net own-screen view (GS/GSPresentView.h), display only. A game patch that draws one view per player may
	// send a finished view picture through main memory and back; with a raised internal resolution it would come
	// back at native sharpness. KeepViewTarget keeps a copy of the frame buffer at BP as it is now (at the
	// renderer's resolution); PasteViewTarget puts that copy into the frame buffer at BP after the game has
	// loaded the native-resolution picture there. Needs proper testing outside Kingdom Hearts II.
	bool KeepViewTarget(u32 BP, u32 PSM);
	bool PasteViewTarget(u32 BP);
	void DropViewTarget();
""")])

edit("pcsx2/GS/Renderers/HW/GSTextureCache.cpp", [(
    """GSTextureCache::Target* GSTextureCache::GetTargetWithSharedBits(u32 BP, u32 PSM) const
{""",
    """// ---------------------------------------------------------------------------------------------------------------
// PS2Net own-screen view: see GSTextureCache.h. The kept copy lives outside the target list (it has no place in
// the emulated graphics memory), so nothing in the emulated machine changes.
namespace
{
	struct KeptViewTarget
	{
		GSTexture* tex = nullptr;
		float scale = 1.0f;
		GSVector2i unscaled = {};
		bool valid_rgb = false;
		bool valid_alpha_low = false;
		bool valid_alpha_high = false;
		bool alpha_range = false;
		int alpha_max = 0;
		int alpha_min = 0;
	};
	KeptViewTarget s_kept_view;
} // namespace

void GSTextureCache::DropViewTarget()
{
	if (s_kept_view.tex && g_gs_device)
		g_gs_device->Recycle(s_kept_view.tex);
	s_kept_view = KeptViewTarget();
}

bool GSTextureCache::KeepViewTarget(u32 BP, u32 PSM)
{
	Target* src = GetTargetWithSharedBits(BP, PSM);
	if (!src || !src->m_texture || src->m_type != RenderTarget || src->m_TEX0.TBP0 != BP)
	{
		DropViewTarget();
		return false;
	}
	src->Update();
	// The copy holds plain alpha values, whatever way the target stores them just now.
	src->UnscaleRTAlpha();
	const GSVector2i size = src->m_texture->GetSize();
	if (s_kept_view.tex && (s_kept_view.tex->GetWidth() != size.x || s_kept_view.tex->GetHeight() != size.y ||
							   s_kept_view.tex->GetFormat() != src->m_texture->GetFormat()))
		DropViewTarget();
	if (!s_kept_view.tex)
		s_kept_view.tex = g_gs_device->CreateRenderTarget(size.x, size.y, src->m_texture->GetFormat(), false);
	if (!s_kept_view.tex)
		return false;
	g_gs_device->CopyRect(src->m_texture, s_kept_view.tex, GSVector4i(0, 0, size.x, size.y), 0, 0);
	s_kept_view.scale = src->m_scale;
	s_kept_view.unscaled = GSVector2i(src->m_valid.z, src->m_valid.w);
	s_kept_view.valid_rgb = src->m_valid_rgb;
	s_kept_view.valid_alpha_low = src->m_valid_alpha_low;
	s_kept_view.valid_alpha_high = src->m_valid_alpha_high;
	s_kept_view.alpha_range = src->m_alpha_range;
	s_kept_view.alpha_max = src->m_alpha_max;
	s_kept_view.alpha_min = src->m_alpha_min;
	return true;
}

bool GSTextureCache::PasteViewTarget(u32 BP)
{
	if (!s_kept_view.tex)
		return false;
	const int w = s_kept_view.unscaled.x;
	const int h = s_kept_view.unscaled.y;
	if (w <= 0 || h <= 0)
		return false;
	const u32 bw = static_cast<u32>((w + 63) / 64);
	// The destination is found, or made, the way a move inside the graphics memory does it (see Move()).
	Target* dst = GetExactTarget(BP, bw, RenderTarget, BP);
	if (!dst)
	{
		GIFRegTEX0 new_TEX0 = {};
		new_TEX0.TBP0 = BP;
		new_TEX0.TBW = bw;
		new_TEX0.PSM = PSMCT32;
		const GSVector2i target_size = GetTargetSize(BP, bw, PSMCT32, Common::AlignUpPow2(w, 64), h);
		dst = LookupDrawTarget(new_TEX0, target_size, s_kept_view.scale, RenderTarget);
		if (!dst)
			dst = Target::Create(new_TEX0, target_size.x, target_size.y, s_kept_view.scale, RenderTarget, true);
		if (!dst)
			return false;
	}
	if (!dst->m_texture || dst->m_scale != s_kept_view.scale)
		return false;
	dst->UpdateValidity(GSVector4i(0, 0, w, h));
	// What the game just loaded (at native resolution) goes into the target first, so it cannot cover the copy later.
	dst->Update();
	dst->UnscaleRTAlpha();
	InvalidateVideoMemType(DepthStencil, dst->m_TEX0.TBP0);
	const int scaled_w = std::min(static_cast<int>(w * s_kept_view.scale), s_kept_view.tex->GetWidth());
	const int scaled_h = std::min(static_cast<int>(h * s_kept_view.scale), s_kept_view.tex->GetHeight());
	if (scaled_w > dst->m_texture->GetWidth() || scaled_h > dst->m_texture->GetHeight())
		return false;
	g_gs_device->CopyRect(s_kept_view.tex, dst->m_texture, GSVector4i(0, 0, scaled_w, scaled_h), 0, 0);
	dst->m_valid_rgb |= s_kept_view.valid_rgb;
	dst->m_valid_alpha_low |= s_kept_view.valid_alpha_low;
	dst->m_valid_alpha_high |= s_kept_view.valid_alpha_high;
	dst->m_alpha_range |= s_kept_view.alpha_range;
	dst->m_alpha_max = s_kept_view.alpha_max;
	dst->m_alpha_min = s_kept_view.alpha_min;
	dst->UpdateValidity(GSVector4i(0, 0, w, h));
	dst->UpdateDrawn(GSVector4i(0, 0, w, h));
	return true;
}

GSTextureCache::Target* GSTextureCache::GetTargetWithSharedBits(u32 BP, u32 PSM) const
{"""),
    ("""GSTextureCache::~GSTextureCache()
{
	RemoveAll(true, true, true);
""",
     """GSTextureCache::~GSTextureCache()
{
	DropViewTarget(); // PS2Net own-screen view
	RemoveAll(true, true, true);
""")])

# ---- state: the two "keep" ids and the place the copy goes back to
edit("pcsx2/GS/GSPresentView.h", [(
    """		// kind 2: at the marker, copy the frame buffer that is on display instead of the one being drawn to
		bool marker_shown_buffer = false;""",
    """		// Any layout: "keep" markers (0 = none). At keep_save_id the frame buffer being drawn to is copied at the
		// renderer's resolution; at keep_restore_id the copy is put into the frame buffer at block keep_restore_bp
		// (the game has just loaded the same picture there at native resolution). Every PC does this.
		u32 keep_save_id = 0;
		u32 keep_restore_id = 0;
		u32 keep_restore_bp = 0;
		// kind 2: at the marker, copy the frame buffer that is on display instead of the one being drawn to
		bool marker_shown_buffer = false;"""),
    ("""	bool MarkerWanted(u32 label_id);""",
     """	bool MarkerWanted(u32 label_id);
	int KeepWanted(u32 label_id, u32* restore_bp); // 0 no, 1 keep a copy now, 2 put the copy back""")])

edit("pcsx2/GS/Renderers/Common/GSRenderer.cpp", [(
    """bool GSPresentView::MarkerOfShownBuffer()
{""",
    """int GSPresentView::KeepWanted(u32 label_id, u32* restore_bp)
{
	if (s_view.keep_save_id != 0 && label_id == s_view.keep_save_id)
		return 1;
	if (s_view.keep_restore_id != 0 && label_id == s_view.keep_restore_id)
	{
		*restore_bp = s_view.keep_restore_bp;
		return 2;
	}
	return 0;
}

bool GSPresentView::MarkerOfShownBuffer()
{""")])

edit("pcsx2/GS/Renderers/HW/GSRendererHW.h", [(
    """	void CaptureViewMarker(bool flush_first, bool shown_buffer);""",
    """	void CaptureViewMarker(bool flush_first, bool shown_buffer);
	// PS2Net own-screen view: keep a copy of the frame buffer being drawn to / put it into the frame buffer at bp.
	void KeepViewPicture(bool save, u32 restore_bp);""")])

edit("pcsx2/GS/Renderers/HW/GSRendererHW.cpp", [(
    """void GSPresentView::OnLabel(u32 label_id)
{
	if (MarkerWanted(label_id) && GSIsHardwareRenderer())
		GSRendererHW::GetInstance()->CaptureViewMarker(true, MarkerOfShownBuffer());
}""",
    """void GSRendererHW::KeepViewPicture(bool save, u32 restore_bp)
{
	// Everything sent so far must be done first: the draws into the picture, and the game's loading of it.
	Flush(GSFlushReason::UNKNOWN);
	if (save)
		g_texture_cache->KeepViewTarget(m_context->FRAME.Block(), m_context->FRAME.PSM);
	else
		g_texture_cache->PasteViewTarget(restore_bp);
}

void GSPresentView::OnLabel(u32 label_id)
{
	if (!GSIsHardwareRenderer())
		return;
	if (MarkerWanted(label_id))
		GSRendererHW::GetInstance()->CaptureViewMarker(true, MarkerOfShownBuffer());
	u32 restore_bp = 0;
	if (const int keep = KeepWanted(label_id, &restore_bp))
		GSRendererHW::GetInstance()->KeepViewPicture(keep == 1, restore_bp);
}""")])

edit("pcsx2/PS2Net/PS2Net.cpp", [(
    """			std::array<u32, kMaxPlayers> marker_ids = {};
			u32 marker_all_id = 0;""",
    """			std::array<u32, kMaxPlayers> marker_ids = {};
			u32 marker_all_id = 0;
			// KeepSaveId / KeepRestoreId / KeepRestoreBlock: see GSPresentView::State.
			u32 keep_save_id = 0;
			u32 keep_restore_id = 0;
			u32 keep_restore_bp = 0;"""),
    ("""				else if (key == "markerallid")
					s_view.marker_all_id = hex;""",
     """				else if (key == "markerallid")
					s_view.marker_all_id = hex;
				else if (key == "keepsaveid")
					s_view.keep_save_id = hex;
				else if (key == "keeprestoreid")
					s_view.keep_restore_id = hex;
				else if (key == "keeprestoreblock")
					s_view.keep_restore_bp = hex;"""),
    ("""			if (s_view.marker_all_id)
				parts += fmt::format(" marker for everybody = {:08X};", s_view.marker_all_id);""",
     """			if (s_view.marker_all_id)
				parts += fmt::format(" marker for everybody = {:08X};", s_view.marker_all_id);
			if (s_view.keep_save_id && s_view.keep_restore_id)
				parts += fmt::format(" keep a picture at {:08X}, put it back at {:08X} into block {:05X};", s_view.keep_save_id,
					s_view.keep_restore_id, s_view.keep_restore_bp);"""),
    ("""				   a.show_copy == b.show_copy && a.marker_id == b.marker_id && a.marker_all_id == b.marker_all_id &&""",
     """				   a.show_copy == b.show_copy && a.marker_id == b.marker_id && a.marker_all_id == b.marker_all_id &&
				   a.keep_save_id == b.keep_save_id && a.keep_restore_id == b.keep_restore_id &&
				   a.keep_restore_bp == b.keep_restore_bp &&"""),
    ("""			want.marker_all_id = s_view.marker_all_id;""",
     """			want.marker_all_id = s_view.marker_all_id;
			want.keep_save_id = s_view.keep_save_id;
			want.keep_restore_id = s_view.keep_restore_id;
			want.keep_restore_bp = s_view.keep_restore_bp;""")])
print("done")
