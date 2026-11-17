// Lane S3: prepare a raw overlay module (imported as a binary at 0x01F18000) for analysis:
// start disassembly at every "addiu sp,sp,-N" (function prologue) and at the entry jump, and create functions.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;

public class S3Prep extends GhidraScript {
    @Override
    public void run() throws Exception {
        Memory mem = currentProgram.getMemory();
        int made = 0;
        for (MemoryBlock b : mem.getBlocks()) {
            if (!b.isInitialized()) continue;
            Address a = b.getStart();
            long n = b.getSize() / 4;
            for (long i = 0; i < n; i++) {
                Address at = a.add(i * 4);
                int w = mem.getInt(at);
                if ((w >>> 16) == 0x27BD && (w & 0x8000) != 0) {
                    disassemble(at);
                    if (getFunctionAt(at) == null) {
                        createFunction(at, null);
                        made++;
                    }
                }
            }
        }
        println("S3Prep: functions created " + made);
    }
}
