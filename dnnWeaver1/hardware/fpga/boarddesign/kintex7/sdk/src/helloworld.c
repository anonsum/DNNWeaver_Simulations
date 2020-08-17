/******************************************************************************
*
* Copyright (C) 2009 - 2014 Xilinx, Inc.  All rights reserved.
*
* Permission is hereby granted, free of charge, to any person obtaining a copy
* of this software and associated documentation files (the "Software"), to deal
* in the Software without restriction, including without limitation the rights
* to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
* copies of the Software, and to permit persons to whom the Software is
* furnished to do so, subject to the following conditions:
*
* The above copyright notice and this permission notice shall be included in
* all copies or substantial portions of the Software.
*
* Use of the Software is limited solely to applications:
* (a) running on a Xilinx device, or
* (b) that interact with a Xilinx device through a bus or interconnect.
*
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
* IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
* FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
* XILINX  BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
* WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF
* OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
* SOFTWARE.
*
* Except as contained in this notice, the name of the Xilinx shall not be used
* in advertising or otherwise to promote the sale, use or other dealings in
* this Software without prior written authorization from Xilinx.
*
******************************************************************************/

/*
 * helloworld.c: simple test application
 *
 * This application configures UART 16550 to baud rate 9600.
 * PS7 UART (Zynq) is not initialized by this application, since
 * bootrom/bsp configures it to baud rate 115200
 *
 * ------------------------------------------------
 * | UART TYPE   BAUD RATE                        |
 * ------------------------------------------------
 *   uartns550   9600
 *   uartlite    Configurable only in HW design
 *   ps7_uart    115200 (configured by bootrom/bsp)
 */

#include <stdio.h>
#include "platform.h"

#include "xil_printf.h"
#include "xil_cache.h"
#include "xio.h"
#include "xuartlite_l.h"
#include "xuartlite.h"
#include "xstatus.h"


#define  START_ADDR XPAR_MIG_7SERIES_0_BASEADDR+0x8000000
#define NUMDATA 64

#define AXI_GP0_MASTER_BASE_ADDR (u32*)XPAR_M_AXI_GP0_BASEADDR
#define AXI_HP0_RD_BASE_ADDR     (u32*)START_ADDR
#define AXI_HP0_WR_BASE_ADDR     (u32*)START_ADDR+100000
//#define UART_BASEADDR            (u32*) XPAR_AXI_UARTLITE_0_BASEADDR

#define WEIGHT_STARTADDR (u32*) 0x88000000
#define WEIGHT_SIZE      888720

#define IMAGE_STARTADDR (u32*) 0x880D8590
#define IMAGE_SIZE      1792

#define NUMD 890512
#define OP_STARTADDR (u32*)0x88169DD0
#define OPSIZE 32/4




///////////////////for uartlite ex case//////////
#define UARTLITE_BASEADDR (u32*) XPAR_AXI_UARTLITE_0_BASEADDR
#define BUFFER_SIZE 16
//int write_to_ddr(u32 uartlite_baseaddress);
 u8 sendbuffer[BUFFER_SIZE];
 u8 recvbuffer[BUFFER_SIZE];


void print(char *str);
void sleep(int count)
{
     int i;
     for(i=0;i<count*10000;i++);
     return;
}

void init_mem (volatile u32* addr, u32 size,u32 data){
	u32 i;

	for(i=0;i<size;i=i+1){
		*(addr+i)=data;

	}
}

void load_mem (volatile u32* addr, u32 size) {
	volatile u32 ptr = addr ;
	    u32 j,i;
	      u8 data[4];
	      u32 data32;
	    for (i=1;i<=size;i++){
	    	j=(i-1)%4;
	    	data[j]=(XUartLite_RecvByte((u32)UARTLITE_BASEADDR));   // No convert from ascii value of "0"
	    	if(j==3){
	    	    data32=(data[0] | (data[1]<<8) | (data[2]<<16) | (data[3]<<24));
	    	    XIo_Out32(ptr,data32);
	    	    ptr=ptr+4;
	    	}
	    }

	    xil_printf("Data32 :%x, i: %d\n\r",data32,i);
}

int main()
{
    init_platform();

    print(" DNNW Classifier System\n\r");
    uint i;
    xil_printf ("==================================================\n\r");

    volatile u32 * control_master = AXI_GP0_MASTER_BASE_ADDR;
    volatile u32 * weight_addr    = WEIGHT_STARTADDR;
    volatile u32* img_addr        = IMAGE_STARTADDR;
    u32 loop;

    u32 w_size= WEIGHT_SIZE;
    u32 i_size= IMAGE_SIZE;
    xil_printf ("Intializing Weights of Size: %x, Addr: %x\n\r", w_size,weight_addr);
    xil_printf ("Send the weights from uart terminal File->Send File \n\r");
    xil_printf ("==================================================\n\r");
    load_mem(weight_addr,w_size);
    u32 donecnt=0;

    for(loop=0;loop<2;loop++){

    	xil_printf("Send image data. Img count :%d \n\r",loop);
    	load_mem(weight_addr+(w_size/4),i_size);
    	xil_printf("Image data loaded\n\r");

     ///////////////////////////// Enabling Accelerator and Waiting for Computation to complete//////////

      *(control_master+0) = 1-*(control_master+0);

      xil_printf ("Waiting for Done from  accelerator\n\r");
      while (*(control_master+1) == donecnt);

      donecnt=donecnt+1;

      xil_printf ("received  Done from  accelerator\n\r");

      // Some issue in the accelerator or sw. Not processing the new image loaded . Reading DDR resolves the issue temporarily.
      for (i=0; i<20000; i++) {
    	  xil_printf("Addr: %x, Data: %x\n\r",weight_addr+i,*(weight_addr+i));
       }

       xil_printf("\n\rAddr: %x, StartCount: %x\n\r",control_master+0,*(control_master+0));
       xil_printf("Addr: %x, 	 Done Count    : %x\n\r",control_master+1,*(control_master+1));


///////////////////////// Final Layer output analysis/////////////////////////////////////////
       short outdata[16];
       short max, index;
       int tmp;
       int j=0;
       i=0;
       max =0;
       for (i=0;i<OPSIZE;i++) {
         tmp=*(OP_STARTADDR+i);
    	 outdata[j]= (short) (tmp & 0xffff);
    	 if(outdata[j]>max) {
    		 max=outdata[j];
    	     index=j;
    	 }
    	 outdata[j+1]= (short) ((tmp & 0xffff0000) >>16);
    	 if(outdata[j+1]>max){
    		max=outdata[j+1];
    	    index=j+1;
       	 }
         j=j+2;
       }

       xil_printf(" Max Value : %x, index:%d\n\r",max,index);
       for(i=0;i<10;i++) {
    	 xil_printf("OutData[%d]:    %d \n\r",i,outdata[i]);
       }
       switch(index){
       case 0 : xil_printf ("--------------The Input Digit is 0 -----------\n\r"); break;
       case 1 : xil_printf ("--------------The Input Digit is 1 -----------\n\r");break;
       case 2 : xil_printf ("--------------The Input Digit is 2 -----------\n\r"); break;
       case 3 : xil_printf ("--------------The Input Digit is 3 -----------\n\r"); break;
       case 4 : xil_printf ("--------------The Input Digit is 4 -----------\n\r"); break;
       case 5 : xil_printf ("--------------The Input Digit is 5 -----------\n\r"); break;
       case 6 : xil_printf ("--------------The Input Digit is 6 -----------\n\r"); break;
       case 7 : xil_printf ("--------------The Input Digit is 7 -----------\n\r"); break;
       case 8 : xil_printf ("--------------The Input Digit is 8 -----------\n\r"); break;
       case 9 : xil_printf ("--------------The Input Digit is 9 -----------\n\r"); break;
       default : xil_printf ("--------------The Input Digit is 0 -----------\n\r"); break;
     }

     sleep(1);
    }

  //////////////////////////////////////////////////////////////////////////////////////////////
   xil_printf("Test Done \n\r");
   return 0;
}


