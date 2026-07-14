---
name: interior-home-staging-director
description: Use this skill when the user wants to redesign, restyle, stage, furnish, declutter, or virtually decorate a real interior photo while preserving the original room geometry and camera view. Trigger this skill for natural requests like "сделай новый дизайн комнаты", "сделай хоумстейджинг", "обнови интерьер", "добавь прикроватные тумбочки", "поставь этот диван в комнату", "положи это покрывало на кровать", "примерь товар с маркетплейса в мой интерьер", "добавь конкретный предмет на это место", or when the user provides a room photo plus a product/reference image and asks to integrate it realistically.
---

# Interior Home Staging Director

## Overview

Turn real interior photos into realistic design, staging, and product-placement edits. Preserve the source room aggressively, then add, replace, or restyle only what the user requested. Use the built-in image editing flow for raster photos.

Treat user images by role:

- Room photo: the edit target and source of perspective, lighting, walls, floor, windows, doors, fixed furniture, and camera angle.
- Product photo: a reference for the exact item to insert, such as a bedspread, bedside table, lamp, chair, rug, sofa, art, curtain, or decor object.
- Style reference: a mood or design direction, not an object to copy exactly.

If no room photo is available, ask for the room photo first. If the user wants a specific marketplace item inserted but only provides the room photo, ask for the product photo or link screenshot.

## Natural Entry Points

Trigger on ordinary phrasing; the user should not need to remember the skill name:

- Russian: "сделай дизайн комнаты", "сделай новый интерьер", "сделай хоумстейджинг", "подготовь комнату к продаже/аренде", "обнови спальню", "добавь тумбочки", "добавь прикроватные тумбочки", "добавь шторы/ковер/лампу/диван/кресло", "поставь это сюда", "примерь это в комнате", "положи это покрывало на кровать", "возьми фото товара и добавь на мое фото", "сделай как на маркетплейсе, но в моей комнате".
- English: "home stage this room", "redesign this interior", "virtually stage this photo", "add these nightstands", "place this product in my room", "put this bedspread on the bed", "try this marketplace item in the room".

## Easy Request Router

Prefer this routing over asking for technical parameters:

- If the user says "сделай дизайн/хоумстейджинг" with only a room photo -> create a tasteful, realistic staged version; keep architecture and camera angle; add plausible furniture/decor only where spatially possible.
- If the user names an object, e.g. "добавь прикроватные тумбочки" -> use insert-only mode: add only that object category unless they also ask for a full redesign.
- If the user asks to change or add a textile, e.g. "поменяй покрывало" or "положи это покрывало на кровать" -> change only the visible textile surface; preserve the bed frame, mattress size, bed height, pillows unless requested, wall color, floor, lighting, and camera angle.
- If the user asks to add one furniture item, e.g. "добавь тумбу" -> add only that item; preserve existing furniture dimensions, bed size, object heights, wall color, floor color, and all existing placements.
- If the user provides a room photo and a product photo -> use the room as the edit target and the product as the insert/reference; match scale, angle, lighting, shadows, fabric folds, occlusion, and contact with surfaces.
- If the user says "сюда", "слева", "справа", "у кровати", "на кровать", "под окно", or marks an area -> place the item there and preserve everything else.
- If the product photo has a white/marketplace background -> ignore the product background and use only the object itself.
- If the product angle is incompatible with the room photo -> still preserve the product's identity, color, material, and proportions, but adapt perspective enough to sit naturally in the room.
- If the requested insert would block a face, person, pet, doorway, safety route, or impossible geometry -> ask one short placement question or choose the nearest plausible spot if obvious.

## Mini Wizard

Ask at most two short questions only when the missing detail blocks a good edit:

- No room photo -> ask for the room photo.
- Product placement requested but no product image -> ask for the product photo or screenshot.
- Room photo exists but placement is ambiguous and multiple placements would change the result materially -> ask: "Куда поставить: слева, справа, у кровати, под окно или на свободную стену?"
- Room redesign requested but no style preference -> choose a warm modern, sale-friendly style by default; do not ask.

## Specific Product Request Recipe

For exact product placement, expect the user to provide two images whenever possible:

1. Room photo: the user's interior photo to edit.
2. Product photo: the exact item to place into the room, such as a bedspread, nightstand, lamp, chair, rug, art, curtain, or decor object.

Use this user intent pattern:

```text
Первое фото - моя комната. Второе фото - конкретный предмет.
Помести [предмет] [точное место] на первом фото.
Остальное не менять: стены, пол, размер кровати, высоту мебели, свет, ракурс и существующие предметы.
```

If the order of images is unclear, ask which image is the room and which image is the product. If the product comes from a marketplace screenshot, use only the object and ignore price labels, buttons, page background, watermarks, ratings, and other UI.

## Operating Contract

Every edit prompt must lock the invariants before describing changes:

- Preserve the original room geometry: walls, floor, ceiling, windows, doors, openings, built-ins, camera angle, lens, crop, and perspective.
- Preserve existing people, pets, personal items, artwork, text, visible brands, and fixed furniture unless the user explicitly asks to remove or replace them.
- Preserve exact room proportions and object proportions: bed width/length/height, mattress height, bedside height references, sofa/chair/table sizes, ceiling height, wall color, floor color, baseboards, and distances between existing objects.
- Preserve lighting direction, shadows, color temperature, reflections, depth of field, and photo realism.
- Add or change only the requested staging/design elements.
- In insert-only or product try-on mode, treat the original photo as locked. Do not redesign, declutter, restyle, resize furniture, recolor walls, recolor floors, change bed dimensions, move existing objects, or adjust object heights.
- Do not widen the room, change window placement, invent new doors, replace flooring/walls, clean clutter, remove objects, repaint, relight, crop, sharpen, upscale, or beautify unless requested.
- For marketplace product insertion, preserve the product's visible identity: shape, color, pattern, material, proportions, decorative details, and recognizable design.
- If exact in-image text or labels are visible on a product, preserve them when possible; warn that generated text may need a retry if the user asks for readable new text.

## Interior Modes

Map simple user words to a practical mode:

- `хоумстейджинг`, `для продажи`, `для аренды` -> sale-friendly staging: brighter, cleaner styling, broad appeal, realistic decor, no luxury overkill.
- `новый дизайн`, `редизайн`, `обнови интерьер` -> tasteful redesign while preserving room architecture.
- `добавь предмет` -> object insertion only.
- `примерь товар`, `с маркетплейса`, `как будет смотреться` -> product try-on compositing.
- `минимально`, `чуть-чуть` -> small additions, 1-3 items.
- `полностью`, `сильно`, `вау` -> richer staging, but still realistic and spatially possible.
- `сканди`, `минимализм`, `современный`, `лофт`, `джапанди`, `классика`, `уютно`, `дорого`, `детская`, `для аренды` -> use that style direction.

## Product Placement Checklist

Before editing, infer or extract:

- target room photo.
- product/reference image, if any.
- requested object category and exact item identity.
- placement zone: bed, wall, floor, bedside, window, table, sofa, corner, shelf, or user-marked area.
- locked dimensions: bed size, wall color, existing furniture heights, floor/wall/ceiling planes, and visible distances between existing objects.
- protected room elements.
- whether this is insert-only, redesign, staging, replacement, or style exploration.

For product inserts:

- Remove the product's marketplace background mentally; do not paste a rectangular screenshot.
- Match the object's scale to nearby furniture and human-room proportions.
- Add realistic contact shadows and occlusion.
- Match fabric behavior when placing textiles: folds, drape, mattress edges, seams, wrinkles, and visible thickness, while preserving the original bed size, mattress height, pillow positions, headboard, and bed frame.
- For bedside tables, match the scale to the existing bed height without changing the bed, mattress, wall, floor, or nearby furniture.
- For rugs, align with floor perspective and place under furniture legs when appropriate.
- For wall art, align with wall plane and preserve perspective.
- For lamps and glossy items, match highlights and shadow direction.

## Prompt Pattern

Use this structure for image edits:

```text
Edit the provided room photo as the exact target. Preserve the original room geometry, camera angle, crop, perspective, walls, floor, ceiling, windows, doors, fixed furniture, people, pets, visible text, lighting direction, shadows, reflections, and background layout. Preserve exact wall color, floor color, bed size, mattress height, existing furniture dimensions, object heights, and distances between existing objects. Do not remove, move, resize, repaint, recolor, relight, crop, widen, beautify, sharpen, or change anything except the requested staging/design elements.

Task: [insert-only / product try-on / home staging / redesign / replacement].

Only add or change: [precise objects, placement, scale, style, material, product identity, and relation to existing furniture]. In insert-only mode, do not alter any other part of the photo.

If using a product reference image: use only the product itself, not its marketplace background. Preserve the product's shape, color, pattern, material, proportions, and recognizable design while adapting perspective and lighting to the room.

Interior direction: [style, audience, mood, budget level, sale/rent/use case].

Match the original lens, perspective, light direction, color temperature, shadows, reflections, depth of field, occlusion, and photo grain. The result must look like a real photo of the same room after staging.

Safety and boundaries: no structural changes, no impossible geometry, no fake windows/doors, no blocked walkways, no distorted furniture, no changed people or pets, no changed wall color, no changed bed size, no changed object heights, no new text unless explicitly requested.
```

## Defaults

When the user gives a loose request:

- task: home staging or object insertion, depending on whether they ask for a full design or a named object.
- style: warm modern, neutral, cozy, sale-friendly.
- budget feel: realistic mid-market, not luxury showroom unless requested.
- changes: preserve architecture, exact wall/floor colors, bed size, object heights, and fixed furniture; add decor, soft goods, lighting, small furniture, rugs, wall art, plants, and storage only where plausible.
- product fidelity: high; preserve pattern, color, proportions, and material of provided product images.

## Quick Examples

- "Вот фото спальни. Сделай хоумстейджинг для аренды" -> warm modern staging, keep room geometry, add plausible bedding/decor/light/rug only.
- "Добавь прикроватные тумбочки по обе стороны кровати" -> insert-only; add matching nightstands, preserve bed, walls, floor, lighting, and camera angle.
- "Вот комната, вот покрывало с маркетплейса. Положи его на кровать" -> product try-on; use the product as a textile reference, drape it naturally on the existing bed, preserve product pattern and color.
- "Поставь этот диван у правой стены" -> product try-on; adapt perspective and scale, add contact shadows, preserve the rest of the room.
- "Сделай новый дизайн, но пол и окна не менять" -> redesign; lock floors and windows explicitly.
