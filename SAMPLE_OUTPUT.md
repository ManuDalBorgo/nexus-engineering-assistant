## 📝 Sample Output

### Example 1: AXI4-Lite Slave Generation (Model: Claude 3.5 Sonnet)

**User Prompt:**
> "Generate an AXI4-Lite slave module"

**Agent Thought Process (Live Stream):**
1.  `🔍 Orchestrator: Analyzing intent...`
2.  `📚 RAG Agent: Searching knowledge base for protocol specs...`
3.  `✅ Found relevant specs: 5. Ordering Model AXI4 supports out-of-order transaction completion...`
4.  `⚙️ RTL Agent: Generating Verilog code...`

**Final Output:**
I'll generate a comprehensive AXI4-Lite slave module for you. This implementation follows the AMBA AXI4-Lite specification with proper handshaking and register interface.

```verilog
//==============================================================================
// AXI4-Lite Slave Module
// Compatible with AMBA AXI4-Lite Protocol Specification
// Author: ARM Solutions Architect
//==============================================================================

module axi4_lite_slave #(
    parameter integer C_S_AXI_DATA_WIDTH = 32,
    parameter integer C_S_AXI_ADDR_WIDTH = 32,
    parameter integer C_NUM_REGISTERS    = 16  // Number of 32-bit registers
)(
    // Global Clock Signal
    input  wire                                S_AXI_ACLK,
    // Global Reset Signal (Active Low)
    input  wire                                S_AXI_ARESETN,

    // Write Address Channel
    input  wire [C_S_AXI_ADDR_WIDTH-1:0]     S_AXI_AWADDR,
    input  wire                                S_AXI_AWVALID,
    output reg                                 S_AXI_AWREADY,

    // Write Data Channel
    input  wire [C_S_AXI_DATA_WIDTH-1:0]     S_AXI_WDATA,
    input  wire [(C_S_AXI_DATA_WIDTH/8)-1:0] S_AXI_WSTRB,
    input  wire                                S_AXI_WVALID,
    output reg                                 S_AXI_WREADY,

    // Write Response Channel
    output reg  [1:0]                          S_AXI_BRESP,
    output reg                                 S_AXI_BVALID,
    input  wire                                S_AXI_BREADY,

    // Read Address Channel
    input  wire [C_S_AXI_ADDR_WIDTH-1:0]     S_AXI_ARADDR,
    input  wire                                S_AXI_ARVALID,
    output reg                                 S_AXI_ARREADY,

    // Read Data Channel
    output reg  [C_S_AXI_DATA_WIDTH-1:0]     S_AXI_RDATA,
    output reg  [1:0]                          S_AXI_RRESP,
    output reg                                 S_AXI_RVALID,
    input  wire                                S_AXI_RREADY
);

    //==========================================================================
    // Local Parameters
    //==========================================================================
    localparam integer ADDR_LSB = (C_S_AXI_DATA_WIDTH/32) + 1;
    localparam integer OPT_MEM_ADDR_BITS = $clog2(C_NUM_REGISTERS) - 1;

    // AXI4 Response Types
    localparam [1:0] RESP_OKAY   = 2'b00;
    localparam [1:0] RESP_EXOKAY = 2'b01;
    localparam [1:0] RESP_SLVERR = 2'b10;
    localparam [1:0] RESP_DECERR = 2'b11;

    //==========================================================================
    // Internal Signals
    //==========================================================================
    reg [C_S_AXI_ADDR_WIDTH-1:0]   axi_awaddr;
    reg                             axi_awready;
    reg                             axi_wready;
    reg [1:0]                       axi_bresp;
    reg                             axi_bvalid;
    reg [C_S_AXI_ADDR_WIDTH-1:0]   axi_araddr;
    reg                             axi_arready;
    reg [C_S_AXI_DATA_WIDTH-1:0]   axi_rdata;
    reg [1:0]                       axi_rresp;
    reg                             axi_rvalid;

    // Memory mapped registers
    reg [C_S_AXI_DATA_WIDTH-1:0] slv_reg [0:C_NUM_REGISTERS-1];

    wire                            slv_reg_rden;
    wire                            slv_reg_wren;
    reg [C_S_AXI_DATA_WIDTH-1:0]   reg_data_out;
    integer                         byte_index;
    reg                             aw_en;

    //==========================================================================
    // I/O Connections assignments
    //==========================================================================
    assign S_AXI_AWREADY = axi_awready;
    assign S_AXI_WREADY  = axi_wready;
    assign S_AXI_BRESP   = axi_bresp;
    assign S_AXI_BVALID  = axi_bvalid;
    assign S_AXI_ARREADY = axi_arready;
    assign S_AXI_RDATA   = axi_rdata;
    assign S_AXI_RRESP   = axi_rresp;
    assign S_AXI_RVALID  = axi_rvalid;

    //==========================================================================
    // Write Address Ready Generation
    // axi_awready is asserted for one S_AXI_ACLK clock cycle when both
    // S_AXI_AWVALID and S_AXI_WVALID are asserted. axi_awready is
    // de-asserted when reset is low.
    //==========================================================================
    always @(posedge S_AXI_ACLK) begin
        if (S_AXI_ARESETN == 1'b0) begin
            axi_awready <= 1'b0;
            aw_en <= 1'b1;
        end else begin
            if (~axi_awready && S_AXI_AWVALID && S_AXI_WVALID && aw_en) begin
                // Slave is ready to accept write address when
                // there is a valid write address and write data
                // on the write address and data bus.
                axi_awready <= 1'b1;
                aw_en <= 1'b0;
            end else if (S_AXI_BREADY && axi_bvalid) begin
                aw_en <= 1'b1;
                axi_awready <= 1'b0;
            end else begin
                axi_awready <= 1'b0;
            end
        end
    end

    //==========================================================================
    // Write Address Latching
    // This process is used to latch the address when both
    // S_AXI_AWVALID and S_AXI_WVALID are valid.
    //==========================================================================
    always @(posedge S_AXI_ACLK) begin
        if (S_AXI_ARESETN == 1'b0) begin
            axi_awaddr <= 0;
        end else begin
            if (~axi_awready && S_AXI_AWVALID && S_AXI_WVALID && aw_en) begin
                // Write Address latching
                axi_awaddr <= S_AXI_AWADDR;
            end
        end
    end

    //==========================================================================
    // Write Data Ready Generation
    // axi_wready is asserted for one S_AXI_ACLK clock cycle when both
    // S_AXI_AWVALID and S_AXI_WVALID are asserted.
    //==========================================================================
    always @(posedge S_AXI_ACLK) begin
        if (S_AXI_ARESETN == 1'b0) begin
            axi_wready <= 1'b0;
        end else begin
            if (~axi_wready && S_AXI_WVALID && S_AXI_AWVALID && aw_en) begin
                // Slave is ready to accept write data when
                // there is a valid write address and write data
                axi_wready <= 1'b1;
            end else begin
                axi_wready <= 1'b0;
            end
        end
    end

    //==========================================================================
    // Memory Mapped Register Select and Write Logic Generation
    // Slave register write enable is asserted when valid address and data
    // are available and the slave is ready to accept the write address and data.
    //==========================================================================
    assign slv_reg_wren = axi_wready && S_AXI_WVALID && axi_awready && S_AXI_AWVALID;

    always @(posedge S_AXI_ACLK) begin
        if (S_AXI_ARESETN == 1'b0) begin
            // Initialize all registers to 0
            for (int i = 0; i < C_NUM_REGISTERS; i++) begin
                slv_reg[i] <= 0;
            end
        end else begin
            if (slv_reg_wren) begin
                // Byte-addressable register write with write strobes
                for (byte_index = 0; byte_index <= (C_S_AXI_DATA_WIDTH/8)-1; byte_index = byte_index+1) begin
                    if (S_AXI_WSTRB[byte_index] == 1) begin
                        slv_reg[axi_awaddr[ADDR_LSB+OPT_MEM_ADDR_BITS:ADDR_LSB]]
                               [(byte_index*8) +: 8] <= S_AXI_WDATA[(byte_index*8) +: 8];
                    end
                end
            end
        end
    end

    //==========================================================================
    // Write Response Logic Generation
    // The write response and response valid signals are asserted by the slave
    // when axi_wready, S_AXI_WVALID, axi_wready and S_AXI_WVALID are asserted.
    //==========================================================================
    always @(posedge S_AXI_ACLK) begin
        if (S_AXI_ARESETN == 1'b0) begin
            axi_bvalid <= 0;
            axi_bresp  <= 2'b0;
        end else begin
            if (axi_awready && S_AXI_AWVALID && ~axi_bvalid && axi_wready && S_AXI_WVALID) begin
                // Indicates a valid write response is available
                axi_bvalid <= 1'b1;
                axi_bresp  <= RESP_OKAY; // 'OKAY' response
            end else begin
                if (S_AXI_BREADY && axi_bvalid) begin
                    // Check if bready is asserted while bvalid is high)
                    axi_bvalid <= 1'b0;
                end
            end
        end
    end

    //==========================================================================
    // Read Address Ready Generation
    // axi_arready is asserted for one S_AXI_ACLK clock cycle when
    // S_AXI_ARVALID is asserted.
    //==========================================================================
    always @(posedge S_AXI_ACLK) begin
        if (S_AXI_ARESETN == 1'b0) begin
            axi_arready <= 1'b0;
            axi_araddr  <= 32'b0;
        end else begin
            if (~axi_arready && S_AXI_ARVALID) begin
                // Indicates that the slave has accepted the valid read address
                axi_arready <= 1'b1;
                // Read address latching
                axi_araddr  <= S_AXI_ARADDR;
            end else begin
                axi_arready <= 1'b0;
            end
        end
    end

    //==========================================================================
    // Read Data Valid Generation
    // axi_rvalid is asserted for one clock cycle when both
    // S_AXI_ARVALID and axi_arready are asserted.
    //==========================================================================
    always @(posedge S_AXI_ACLK) begin
        if (S_AXI_ARESETN == 1'b0) begin
            axi_rvalid <= 0;
            axi_rresp  <= 0;
        end else begin
            if (axi_arready && S_AXI_ARVALID && ~axi_rvalid) begin
                // Valid read data is available at the read data bus
                axi_rvalid <= 1'b1;
                axi_rresp  <= RESP_OKAY; // 'OKAY' response
            end else if (axi_rvalid && S_AXI_RREADY) begin
                // Read data is accepted by the master
                axi_rvalid <= 1'b0;
            end
        end
    end

    //==========================================================================
    // Memory Mapped Register Select and Read Logic Generation
    // Slave register read enable is asserted when valid address is available
    // and the slave is ready to accept the read address.
    //==========================================================================
    assign slv_reg_rden = axi_arready & S_AXI_ARVALID & ~axi_rvalid;

    always @(*) begin
        // Address decoding for reading registers
        reg_data_out = slv_reg[axi_araddr[ADDR_LSB+OPT_MEM_ADDR_BITS:ADDR_LSB]];
    end

    // Output register or memory read data
    always @(posedge S_AXI_ACLK) begin
        if (S_AXI_ARESETN == 1'b0) begin
            axi_rdata <= 0;
        end else begin
            // When there is a valid read address (S_AXI_ARVALID) with
            // acceptance of read address by the slave (axi_arready),
            // output the read data
            if (slv_reg_rden) begin
                axi_rdata <= reg_data_out; // register read data
            end
        end
    end

endmodule
```

**Key Features of this AXI4-Lite Slave Implementation:**
*   **Protocol Compliance**:
    *   No ID signals - All transactions are in-order as per AXI4-Lite spec
    *   Burst length of 1 - Single beat transactions only
    *   Full data width access - Data accesses match bus width
    *   Proper handshaking - VALID/READY protocol on all channels
*   **Functional Highlights**:
    *   Configurable Parameters - Data width, address width, and register count
    *   Byte-addressable Writes - Uses WSTRB for partial byte writes
    *   Memory-mapped Registers - Parameterizable number of control registers
    *   Proper Reset Handling - Active-low reset with proper initialization
    *   Response Generation - OKAY responses for successful transactions
*   **Channel Implementation**:
    *   Write Address Channel - Latches address when both AWVALID and WVALID
    *   Write Data Channel - Synchronized with address channel
    *   Write Response Channel - Provides completion acknowledgment
    *   Read Address Channel - Single-cycle address acceptance
    *   Read Data Channel - Registered output with proper timing

This implementation is suitable for control register interfaces, configuration registers, or any simple memory-mapped peripheral requiring AXI4-Lite connectivity.
