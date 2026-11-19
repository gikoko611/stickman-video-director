# G.I KO KO — The Missing Calf (Myanmar Cinematic Render)

This production preset renders a 3-minute, 854×480 MP4 with English multi-character Deepgram Aura-2 dialogue and Burmese subtitles.

## Required GitHub Secret

In this repository, open **Settings → Secrets and variables → Actions → New repository secret**:

- Name: `DEEPGRAM_API_KEY`
- Secret: your Deepgram API key

Never put the key in source code, workflow inputs, or chat. The workflow checks only whether the secret exists; it never prints the value.

The renderer uses role-specific English Aura-2 voices:
- Narrator: `aura-2-thalia-en`
- Min Thu: `aura-2-orion-en`
- Mother: `aura-2-luna-en`
- Friend: `aura-2-zeus-en`
- Farmer: `aura-2-asteria-en`

Deepgram Aura-2 voices synthesize English dialogue. Burmese is provided as timed, authored subtitles; this workflow does not claim Burmese Deepgram speech support.

## Start a render

1. Open the repository's **Actions** tab.
2. Select **Myanmar Cinematic Story Render**.
3. Press **Run workflow** on branch `main`.
4. Choose `balanced` (recommended) or `compact`.
5. Wait for the job to finish, then download the artifact named `GI-KO-KO-Myanmar-Village-Cinematic-480p`.

The artifact contains:
- `GI-KO-KO-Myanmar-Village-Cinematic-480p.mp4`
- `subtitles-my.srt`
- `production-report.json`

## Output contract

- Runtime: 180 seconds
- Resolution: 854×480
- Frame rate: 12 fps
- Container/video: MP4 / H.264
- Audio: AAC mono
- Subtitle: Burmese, burned into the MP4 and supplied as SRT
- File size: hard validation below 10,000,000 bytes; a second lower-bitrate encode is attempted if needed.

The visual implementation is an original **cinematic illustrated 2.5D treatment** with layered Myanmar village scenery, character staging, and slow camera moves. It is not a fully rigged 3D/Blender character animation. The strict 10 MB cap also requires a compact 480p/12 fps encode.

## Troubleshooting

- If the job reports a missing key, add the repository secret exactly as `DEEPGRAM_API_KEY`.
- If Deepgram returns 401/402/403, check key validity, account balance/credits, and access to the configured Aura-2 voices.
- If a configured voice is unavailable to the project, update its model ID in `render.py` to a voice enabled in the Deepgram project.
- If the output cannot meet the 10 MB cap, the job fails rather than uploading an oversized MP4.
