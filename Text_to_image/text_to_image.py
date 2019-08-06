from PIL import Image, ImageFont, ImageDraw


def text_to_png(text):
    i = Image.new('RGB', (535, 300), (255, 255, 255))
    d = ImageDraw.Draw(i)
    f = ImageFont.truetype('fonts/SourceHanSansSC-Medium.otf', 54)

    # ascent, descent = f.getmetrics()
    # (width, baseline), (offset_x, offset_y) = f.font.getsize(text)
    # left, top, right, bottom = f.getmask(text).getbbox()
    # d.rectangle((left, top, right, bottom), (0, 0, 0))

    d.text((50, 40), text, font=f, fill='#000000', align='center')
    i.save('t.png')


if __name__ == '__main__':
    t = '甄士隐梦幻识通灵 贾雨村风尘怀闺秀'
    text_to_png(t.replace(' ', '\n\n'))