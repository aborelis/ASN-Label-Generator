#!/usr/bin/env python3

from functools import partial

import AveryLabels
from AveryLabels import labelInfo
from reportlab.lib.units import mm
from reportlab.lib.units import toLength
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab_qrcode import QRCodeImage

# from reportlab.graphics import shapes

from clize import run


project_homepage = "https://github.com/aborelis/ASN-Label-Generator"


class LabelContext:

    def __init__(self, data):

        self.filename = None

        self.labeltype = 4731
        self.number = 189

        self.num_digits = 6
        self.first_asn = 1

        self.offset = 0

        self.font_size = 2 * mm
        self.qr_size = 0.9
        self.qr_margin = 1 * mm

        self.sub_labels_x = 1
        self.sub_labels_y = 1

        self.debug = False
        self.position_helper = False

        self.bar_width = 0
        self.bar_color = HexColor("#d2dede")
        self.highlight_bar_width = 0
        self.highlight_bar_color = HexColor("#d9a4a6")
        self.prefix = "ASN"

        self.__dict__.update(data)

        self.current_asn = self.first_asn

    def incASN(self):
        self.current_asn = self.current_asn + 1


def render(context: LabelContext, c: canvas.Canvas, width: float, height: float):

    sub_label_width = width / context.sub_labels_x
    sub_labelheight = height / context.sub_labels_y

    for i in range(context.sub_labels_x):
        for j in range(context.sub_labels_y - 1, -1, -1):  # no idea why inverted...
            sub_x = sub_label_width * i
            sub_y = sub_labelheight * j

            c.saveState()
            c.translate(sub_x, sub_y)

            # barcode_value = f"ASN{currentASN:06d}"
            barcode_value = context.prefix + str(context.current_asn).zfill(
                context.num_digits
            )
            context.incASN()

            qr = QRCodeImage(barcode_value, size=sub_labelheight * context.qr_size)
            qr.drawOn(
                c, x=context.qr_margin, y=sub_labelheight * ((1 - context.qr_size) / 2)
            )
            c.setFont("Helvetica", size=context.font_size)
            c.drawString(
                x=sub_labelheight,
                y=(sub_labelheight - context.font_size) / 2,
                text=barcode_value,
            )

            if context.bar_width > 0:
                c.setFillColor(context.bar_color)
                c.rect(
                    sub_label_width - context.bar_width,
                    0,
                    context.bar_width,
                    sub_labelheight,
                    0,
                    1,
                )
            if context.highlight_bar_width > 0:
                c.setFillColor(context.highlight_bar_color)
                c.rect(
                    sub_label_width - context.bar_width - context.highlight_bar_width,
                    0,
                    context.highlight_bar_width,
                    sub_labelheight,
                    0,
                    1,
                )

            if context.position_helper:
                r = 0.1
                d = 0
                if context.debug:
                    r = 0.5
                    d = r
                c.circle(x_cen=0 + d, y_cen=0 + d, r=r, stroke=1)
                c.circle(x_cen=sub_label_width - d, y_cen=0 + d, r=r, stroke=1)
                c.circle(x_cen=0 + d, y_cen=sub_labelheight - d, r=r, stroke=1)
                c.circle(
                    x_cen=sub_label_width - d, y_cen=sub_labelheight - d, r=r, stroke=1
                )

            c.restoreState()


def generate(
    filename=None,
    *,
    labeltype: "l" = "4731",
    number: "n" = 189,  # type: ignore
    offset: "o" = 0,  # type: ignore
    num_digits: "d" = 6,  # type: ignore
    first_asn: "s" = 1,  # type: ignore
    font_size: "f" = "2mm",  # type: ignore
    qr_size: "q" = 0.9,  # type: ignore
    qr_margin: "m" = "1mm",  # type: ignore
    sub_labels_x: "lx" = 1,  # type: ignore
    sub_labels_y: "ly" = 1,  # type: ignore
    debug=False,
    position_helper=False,
    bar_width: "bw" = 0,  # type: ignore
    bar_color: "bc" = "d2dede",  # type: ignore
    highlight_bar_width: "hw" = 0,  # type: ignore
    highlight_bar_color: "hc" = "d9a4a6",  # type: ignore
    prefix: "p" = "ASN",  # type: ignore
):
    """ASN Label Generator

    :param filename: output filename of PDF file generated
    :param labeltype: Type of label, e.g. 4731, get a list of supported labels with --labels
    :param number: number of labels to generate

    :param offset: Number of labels to skip on the first sheet (e.g. already used)
    :param num_digits: Number of digits for the ASN, e.g. 000001
    :param first_asn: First ASN to use, e.g. 100001


    :param font_size: Fontsize with a unit, e.g. 2mm, 0.4cm
    :param qr_size: Size of the QR-Code as percentage of the label hight
    :param qr_margin: Margin around the QR-Code with a unit, e.g. 1mm

    :param sub_labels_x: How many labels to put on a phyical label horizontally
    :param sub_labels_y: How many labels to put on a phyical label vertically

    :param debug: enable debug mode
    :param position_helper: enable position helpers, e.g. as cutting guides when using sub labels



    :param bar_width: Show a colored bar on the right of the label (0 = no bar)
    :param bar_color: Color of the bar, HEX notation
    :param highlight_bar_width: add a colored highlight bar on the right of the label (0 = no bar)
    :param highlight_bar_color: Color of the highlight bar, HEX notation

    :param prefix: Prefix to the actual ASN number

    """

    parm = locals()
    parm["font_size"] = toLength(parm["font_size"])
    parm["qr_margin"] = toLength(parm["qr_margin"])
    parm["bar_color"] = HexColor("#" + parm["bar_color"])
    parm["highlight_bar_color"] = HexColor("#" + parm["highlight_bar_color"])
    parm["labeltype"] = int(parm["labeltype"])

    if parm["filename"] is None:
        parm["filename"] = (
            "label-"
            + str(parm["labeltype"])+ "-"
            + parm["prefix"]+ "-"
            + str(parm["first_asn"]).zfill(parm["num_digits"])+ "-"
            + str(parm["first_asn"] + parm["number"]).zfill(parm["num_digits"])
            + ".pdf"
        )

    context = LabelContext(parm)

    label = AveryLabels.AveryLabel(context.labeltype)

    label.debug = context.debug

    label.open(context.filename)

    render_func = partial(render, context)
    label.render(render_func, count=context.number, offset=context.offset)
    label.close()

    print(f"Output written to {context.filename}")


def labels():
    """Shows a list of supported labels"""
    print("Supported Labels: " + ", ".join(map(str, labelInfo.keys())))


def version():
    """Show the version"""
    return "ASN Label Generator - version 0.1 \n" + project_homepage


def main():
    run(generate, alt=[labels, version])


if __name__ == "__main__":
    main()
