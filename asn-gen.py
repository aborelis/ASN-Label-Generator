#!/usr/bin/env python3

import os
import sys

import AveryLabels
from AveryLabels import labelInfo
from reportlab.lib.units import mm
from reportlab.lib.units import toLength
from reportlab_qrcode import QRCodeImage
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
#from reportlab.graphics import shapes

from clize import ArgumentError, Parameter, run


from functools import partial
import inspect

project_homepage = 'https://github.com/aborelis/ASN-Label-Generator'


class LabelContext:

    
    def __init__(self, data):
        
        self.label = 4731
        self.number =189

        numDigits = 6
        self.firstAsn = 1

        self.offset = 0

        self.fontSize=2*mm
        self.qrSize = 0.9
        self.qrMargin = 1*mm

        self.subLabelsX = 1
        self.subLabelsY = 1
        
        self.debug = False        
        self.positionHelper = False

        

        self.barWidth=0
        self.barColor= HexColor('#d2dede') 
        self.highlightBarWidth = 0 
        self.highlightBarColor= HexColor('#d9a4a6')
        self.prefix='ASN'

        self.__dict__.update(data)    
 
        self.currentASN = self.firstAsn
   

    def incASN(self):
        self.currentASN = self.currentASN + 1





def render(context: LabelContext , c: canvas.Canvas, width: float, height: float):
     

        subLabelWidth = width/context.subLabelsX
        subLabelHeight = height/context.subLabelsY

        for i in range(context.subLabelsX):
            for j in range(context.subLabelsY-1, -1, -1):  # no idea why inverted...
                subX = subLabelWidth*i
                subY = subLabelHeight*j

                c.saveState()
                c.translate(subX, subY)
        
                # barcode_value = f"ASN{currentASN:06d}"
                barcode_value = context.prefix+str(context.currentASN).zfill(context.numDigits)
                context.incASN()

                qr = QRCodeImage(barcode_value, size=subLabelHeight*context.qrSize)
                qr.drawOn(c, x=context.qrMargin, y=subLabelHeight*((1-context.qrSize)/2))
                c.setFont("Helvetica", size=context.fontSize)
                c.drawString(x=subLabelHeight, y=(
                    subLabelHeight-context.fontSize)/2, text=barcode_value)
                
                if context.barWidth > 0 :
                    c.setFillColor(context.barColor)
                    c.rect(subLabelWidth-context.barWidth, 0, context.barWidth, subLabelHeight,0, 1)                    
                if context.highlightBarWidth > 0 :
                    c.setFillColor(context.highlightBarColor)
                    c.rect(subLabelWidth-context.barWidth-context.highlightBarWidth, 0, context.highlightBarWidth, subLabelHeight,0, 1)



                if context.positionHelper:
                    r = 0.1
                    d = 0
                    if context.debug:
                        r = 0.5
                        d = r
                    c.circle(x_cen=0+d, y_cen=0+d, r=r, stroke=1)
                    c.circle(x_cen=subLabelWidth-d, y_cen=0+d, r=r, stroke=1)
                    c.circle(x_cen=0+d, y_cen=subLabelHeight-d, r=r, stroke=1)
                    c.circle(x_cen=subLabelWidth-d,
                                y_cen=subLabelHeight-d, r=r, stroke=1)

                c.restoreState()




def generate( filename = None, *, labeltype:'l' = '4731', 
    number:'n'= 189, 
    offset:'o' = 0, 
    numDigits:'d'= 6, 
    firstAsn:'s' = 1,
    fontSize:'f' = '2mm',
    qrSize:'q' = 0.9,
    qrMargin:'m' = '1mm',

    subLabelsX:'lx' = 1,
    subLabelsY:'ly' = 1,
        
    debug = False ,
    positionHelper = False,

        

    barWidth:'bw'=0,
    barColor:'bc'= 'd2dede',
    highlightBarWidth:'hw'= 0 ,
    highlightBarColor:'hc'= 'd9a4a6',
    prefix:'p' = 'ASN'
):         
    """ASN Label Generator
  
    :param filename: output filename of PDF file generated
    :param labeltype: Type of label, e.g. 4731, get a list of supported labels with --labels
    :param number: number of labels to generate

    :param offset: Number of labels to skip on the first sheet (e.g. already used)
    :param numDigits: Number of digits for the ASN, e.g. 000001
    :param firstAsn: First ASN to use, e.g. 100001
    
    
    :param fontSize: Fontsize with a unit, e.g. 2mm, 0.4cm
    :param qrSize: Size of the QR-Code as percentage of the label hight
    :param qrMargin: Margin around the QR-Code with a unit, e.g. 1mm

    :param subLabelsX: How many labels to put on a phyical label horizontally 
    :param subLabelsY: How many labels to put on a phyical label vertically 
        
    :param debug: enable debug mode
    :param positionHelper: enable position helpers, e.g. as cutting guides when using sub labels

        

    :param barWidth: Show a colored bar on the right of the label (0 = no bar)
    :param barColor: Color of the bar, HEX notation
    :param highlightBarWidth: add a colored highlight bar on the right of the label (0 = no bar)
    :param highlightBarColor: Color of the highlight bar, HEX notation
    
    :param prefix: Prefix to the actual ASN number

    """

    parm = locals()
    parm['fontSize'] = toLength(parm['fontSize'])
    parm['qrMargin'] = toLength(parm['qrMargin'])
    parm['barColor'] = HexColor('#'+parm['barColor'])
    parm['highlightBarColor'] = HexColor('#'+parm['highlightBarColor'])
    parm['labeltype'] = int(parm['labeltype'])

    if parm['filename'] == None:
        parm['filename']= 'label-'+str(parm['labeltype'])+'-'+parm['prefix']+'-'+str(parm['firstAsn']).zfill(parm['numDigits'])+'-'+str(parm['firstAsn']+parm['number']).zfill(parm['numDigits'])+'.pdf'

    context = LabelContext(parm)


    label = AveryLabels.AveryLabel(context.labeltype)

    label.debug = context.debug
    
    label.open(context.filename)

    render_func = partial(render, context)
    label.render(render_func, count=context.number, offset=context.offset)
    label.close()

    print
    print(f"Output written to {context.filename}")



def labels():
    """ Shows a list of supported labels
    """
    print('Supported Labels: '+', '.join(map(str,labelInfo.keys())))


def version():
    """Show the version"""
    return 'ASN Label Generator - version 0.1 \n' + project_homepage


def main():
  run(generate, alt=[labels,version])

if __name__ == '__main__':
  main()