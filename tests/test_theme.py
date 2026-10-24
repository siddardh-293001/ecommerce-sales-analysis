from src import theme

def luminance(color):
    values=[int(color[i:i+2],16)/255 for i in (1,3,5)]
    linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in values]
    return sum(x*y for x,y in zip(linear,[.2126,.7152,.0722]))

def test_body_text_meets_aa():
    for foreground in [theme.TEXT,theme.TEXT_MUTED]:
        for background in [theme.BACKGROUND,theme.SURFACE,theme.SIDEBAR]:
            assert (luminance(background)+.05)/(luminance(foreground)+.05)>=4.5
