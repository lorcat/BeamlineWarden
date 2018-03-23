__author__ = "Konstantin Glazyrin (lorcat@gmail.com)"

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


def pil_text_dict(text, pos, color, font):
    """
    Prepares a dictionary with values for the drawn text
    :param text:
    :param pos:
    :param color:
    :param font:
    :return:
    """
    return {"text": text, "pos": pos, "color": color, "font": font}

def pil_draw_text(draw, text):
    """
    Draws a text based on a certain dictionary
    :param text:
    :param pos:
    :param color:
    :param font:
    :return:
    """
    text, pos, color, font = text["text"], text["pos"], text["color"], text["font"]
    draw_font = ImageFont.truetype(*font)
    draw.text(pos, text, color, font=draw_font)


def pil_report_petra_msg(fntmpl, fnoutput, texts, logger):
    """
    Creates an image with an ok message
    :return:
    """
    img = Image.open(fntmpl)
    draw = ImageDraw.Draw(img)

    for text in texts:
        pil_draw_text(draw, text)

    logger.debug("Trying to save the updated image ({})".format(fnoutput))
    img.save(fnoutput)
    img.close()