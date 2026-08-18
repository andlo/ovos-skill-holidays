"""Generates icon.png - 512x512, rounded-rect background (radius 90),
white line-art calendar with one highlighted date, matching the style
of ovos-skill-geometry/-geography's icons. A calendar page (rather
than a cross, tree, or egg) is deliberately generic across the
holidays this skill covers (Christmas, Easter, national days,
Halloween, ...) - no single religious/cultural symbol represents all
of them."""

from PIL import Image, ImageDraw

SIZE = 512
BG_COLOR = (30, 136, 130, 255)  # a calendar-ish teal, distinct from
                                 # geometry's purple and geography's
                                 # existing color choices
WHITE = (255, 255, 255, 255)

img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)
draw.rounded_rectangle([0, 0, SIZE - 1, SIZE - 1], radius=90, fill=BG_COLOR)

# Calendar body
body_left, body_right = 120, 392
body_top, body_bottom = 160, 400
line_w = 14

draw.rounded_rectangle(
    [body_left, body_top, body_right, body_bottom],
    radius=20, outline=WHITE, width=line_w,
)

# Two hanging rings at the top
ring_w = 16
draw.rounded_rectangle([170, 110, 170 + ring_w, 180], radius=8, fill=WHITE)
draw.rounded_rectangle([342 - ring_w, 110, 342, 180], radius=8, fill=WHITE)

# Header bar (the darker strip at the top of a calendar page)
draw.line([body_left + line_w // 2, 220, body_right - line_w // 2, 220],
           fill=WHITE, width=line_w)

# A 3x3 grid of small day-squares below the header
grid_left = body_left + 34
grid_top = 250
cell = 42
gap = 20
highlight_row, highlight_col = 1, 2  # the "marked" holiday date

for row in range(3):
    for col in range(3):
        x0 = grid_left + col * (cell + gap)
        y0 = grid_top + row * (cell + gap)
        x1, y1 = x0 + cell, y0 + cell
        if (row, col) == (highlight_row, highlight_col):
            draw.rounded_rectangle([x0, y0, x1, y1], radius=8, fill=WHITE)
        else:
            draw.rounded_rectangle([x0, y0, x1, y1], radius=8, outline=WHITE, width=6)

img.save("icon.png")
print("wrote icon.png", img.size, img.mode)
