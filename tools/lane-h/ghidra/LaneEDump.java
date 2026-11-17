// Lane E (copy of lane A script): dump functions (decompiled C, optional assembly, callers) to a text file.
// Script args: <outFile> <item> [<item> ...]
//   item = HEXADDR            function containing that address
//        = HEXSTART-HEXEND    every function whose entry is in the range
//        = callers:HEXADDR    every function that calls the function at that address
//        = asm                also print the assembly of each function
//        = nodecomp           skip decompilation (list + callers only)
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressFactory;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.LinkedHashSet;
import java.util.Set;
import java.util.TreeSet;

public class LaneEDump extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        PrintWriter out = new PrintWriter(new FileWriter(args[0]));
        AddressFactory af = currentProgram.getAddressFactory();
        FunctionManager fm = currentProgram.getFunctionManager();
        boolean asm = false, decomp = true;
        Set<Function> funcs = new LinkedHashSet<>();
        for (int i = 1; i < args.length; i++) {
            String a = args[i];
            if (a.equals("asm")) { asm = true; continue; }
            if (a.equals("nodecomp")) { decomp = false; continue; }
            if (a.startsWith("callers:")) {
                Address t = af.getAddress(a.substring(8));
                Function target = fm.getFunctionContaining(t);
                Address entry = target != null ? target.getEntryPoint() : t;
                ReferenceIterator it = currentProgram.getReferenceManager().getReferencesTo(entry);
                while (it.hasNext()) {
                    Reference r = it.next();
                    Function f = fm.getFunctionContaining(r.getFromAddress());
                    if (f != null) funcs.add(f);
                    else out.println("// reference to " + entry + " from " + r.getFromAddress() + " (" + r.getReferenceType() + ") is outside any function");
                }
            } else if (a.contains("-")) {
                String[] p = a.split("-");
                AddressSet set = new AddressSet(af.getAddress(p[0]), af.getAddress(p[1]));
                for (Function f : fm.getFunctions(set, true)) funcs.add(f);
            } else {
                Function f = fm.getFunctionContaining(af.getAddress(a));
                if (f != null) funcs.add(f);
                else out.println("// no function contains " + a);
            }
        }
        DecompInterface dec = new DecompInterface();
        dec.openProgram(currentProgram);
        for (Function f : funcs) {
            out.println("================================================================");
            out.println("FUNCTION " + f.getName() + " @ " + f.getEntryPoint() + "  body " + f.getBody().getMinAddress() + "-" + f.getBody().getMaxAddress()
                + "  size " + f.getBody().getNumAddresses());
            Set<String> callers = new TreeSet<>();
            ReferenceIterator it = currentProgram.getReferenceManager().getReferencesTo(f.getEntryPoint());
            int n = 0;
            while (it.hasNext()) {
                Reference r = it.next();
                Function c = fm.getFunctionContaining(r.getFromAddress());
                callers.add((c != null ? c.getName() : "?") + "@" + r.getFromAddress() + "(" + r.getReferenceType() + ")");
                n++;
            }
            out.println("REFERENCES TO IT: " + n);
            int shown = 0;
            for (String c : callers) { if (shown++ < 80) out.println("   " + c); }
            if (decomp) {
                DecompileResults res = dec.decompileFunction(f, 60, monitor);
                if (res != null && res.decompileCompleted()) out.println(res.getDecompiledFunction().getC());
                else out.println("// decompile failed: " + (res != null ? res.getErrorMessage() : "null"));
            }
            if (asm) {
                InstructionIterator ii = currentProgram.getListing().getInstructions(f.getBody(), true);
                while (ii.hasNext()) {
                    Instruction ins = ii.next();
                    out.println("  " + ins.getAddress() + "  " + ins.toString());
                }
            }
        }
        out.close();
        println("LaneEDump: " + funcs.size() + " functions -> " + args[0]);
    }
}
