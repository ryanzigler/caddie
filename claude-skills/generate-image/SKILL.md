---
name: generate-image
description: Generate a raster image (PNG) by asking ChatGPT through the local Codex CLI, then wait for it and look at the result. Use whenever the user wants a picture made — a logo, icon, mascot, avatar, illustration, hero or banner image, OG/social card, mockup, concept art, texture, sprite, wallpaper, or "show me what X would look like" — or when a task you're doing needs one, such as placeholder art for a page or a reference image to design from. Not for charts, diagrams, SVG, or anything better drawn in code.
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/generate-image.sh *)
---

# Generate an image

You cannot draw pixels yourself, but this machine has the Codex CLI logged in to the
user's ChatGPT subscription, and ChatGPT can. The bundled script sends ChatGPT your
prompt, waits for its `image_generation` tool to finish, and copies the PNG to the path
you choose. You stay the art director: you write the brief and judge the result.

A call usually takes under a minute, sometimes a few. It uses the user's ChatGPT quota, not
API credits.

## 1. Write the brief

ChatGPT's image model rewards dense, art-directed prompts. A terse prompt yields a
generic image. Cover, in plain sentences:

- **Subject and composition**: what is in frame, where, at what scale, from what angle.
- **Style**: photo, flat vector, 3D render, watercolor, pixel art. Name a medium or
  era instead of "nice" or "modern".
- **Light, palette, mood**: name colors as hex codes when they come from the project.
- **Text in the image**: quote it exactly, or say "no text".
- **Use**: "app icon on a white background", "website hero with empty space on the
  left for a headline". This steers the framing more than any adjective.

Pull concrete details from the project when they exist: brand colors from CSS
variables or a theme file, the product name, the audience.

## 2. Pick the output path and size

Use an absolute path. Kept assets go where the project already keeps images
(`public/`, `assets/`, `static/`, `images/`), named for their purpose, such as
`hero-onboarding.png`. Throwaway explorations go in `/tmp/`. If the file already exists,
pick a new name so you don't overwrite the user's work.

Pass `--size WxH` only when the layout needs an aspect ratio: `1024x1024` square,
`1536x1024` landscape, `1024x1536` portrait. Otherwise let the model choose. The model
treats size as a guide to aspect ratio, so the pixel dimensions can differ. When exact
dimensions matter, resize the result afterward (`sips -z <h> <w>` on macOS).

To edit, restyle, or match an existing image, pass it with `--ref <path>`, which you can
repeat. Say in the brief how to use it: "keep the logo's shape, change the palette to…".

## 3. Send it and wait

Run the script in the foreground with the Bash tool and `timeout: 600000`. The call
blocks until ChatGPT returns the image, which is the wait:

```bash
"${CLAUDE_SKILL_DIR}/scripts/generate-image.sh" "<brief>" /absolute/path/out.png [--size WxH] [--ref /path/ref.png]
```

Stay in the call until it returns. Your turn holds the job: if the turn ends while
the image is still generating, a headless or subagent session exits and takes the job
with it, and the image never lands.

For several images, such as variations to choose from, send them in one Bash call so
they generate in parallel and the call returns when the last one finishes. Check the
output for each path, since one can fail while the others succeed:

```bash
"${CLAUDE_SKILL_DIR}/scripts/generate-image.sh" "<brief A>" /abs/a.png & "${CLAUDE_SKILL_DIR}/scripts/generate-image.sh" "<brief B>" /abs/b.png & wait
```

## 4. Look at it

On success the script prints the absolute path of each PNG. `Read` every one. You can
see images, and this step is why the bridge exists: check each result against the brief
before you call it done.

- **It matches**: show it to the user with a Markdown image, `![alt](/absolute/path.png)`,
  and give its path. If it feeds other work, such as wiring a hero image into a page,
  carry on with that work.
- **It misses something the user asked for** (wrong text, missing subject, wrong
  aspect): regenerate once with the brief rewritten to name the miss explicitly. If the
  second try also misses, show the user what you have and say what's off. Rerolling
  further spends their quota on luck.
- **Taste calls** (color, mood, composition the brief left open): show the image and let
  the user steer. Don't silently reroll.

## When the script fails

It exits nonzero with a message and the tail of the Codex log on stderr:

| Message | What to do |
| --- | --- |
| `codex CLI not found` | Tell the user to install Codex (`brew install codex`) and run `codex login`. |
| `codex is not logged in` | Tell the user to run `codex login` with their ChatGPT account. |
| `finished without generating an image` | Read the log tail. A refusal means rewording the brief; a usage-limit message means the quota is spent, so tell the user and stop. |
| `codex exec failed` | Report the log tail. Retry once only if it looks transient (network, timeout). |
