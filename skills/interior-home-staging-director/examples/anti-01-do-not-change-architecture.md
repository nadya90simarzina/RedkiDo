# Anti-Example: Do Not Change Architecture

## Input

Сделай новый дизайн гостиной, но только мебель и декор. Планировку, окна, двери и пол не трогать.

## Expected Behavior

Lock the room architecture explicitly before editing. Add or replace only movable furniture and decor if requested. Keep the original walls, floor, windows, doors, openings, built-ins, camera angle, crop, and perspective unchanged.

## Must Not

Do not create new windows, move doors, change flooring, alter ceiling height, widen the room, change wall geometry, or make an architectural renovation unless the user explicitly asks for it.
