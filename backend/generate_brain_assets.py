#!/usr/bin/env python3
"""
Generate brain mesh assets for the TRIBE 3D Brain Viewer.
Run once — creates static files for the Next.js app.

Outputs:
  - fsaverage5_inflated.glb   (~500 KB, inflated brain surface)
  - fsaverage5_pial.glb       (~500 KB, realistic brain surface)
  - brain_atlas.json           (~200 KB, vertex → region mapping)
  - brain_regions.json         (region metadata: name, function, emotion, marketing use)

These go into the Next.js public/brain/ directory.
"""

import json
import numpy as np

# Output directory
OUTPUT_DIR = "brain_assets"


def generate_meshes():
    """Generate GLB mesh files from fsaverage5."""
    import nibabel as nib
    import trimesh
    from nilearn.datasets import fetch_surf_fsaverage

    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Fetching fsaverage5 mesh data...")
    fsaverage5 = fetch_surf_fsaverage(mesh="fsaverage5")

    for surface_name, left_key, right_key in [
        ("inflated", "infl_left", "infl_right"),
        ("pial", "pial_left", "pial_right"),
    ]:
        print(f"Processing {surface_name} surface...")
        # GIFTI format (.gii.gz) — use nibabel.load, not read_geometry
        gii_l = nib.load(fsaverage5[left_key])
        coords_l = gii_l.darrays[0].data  # vertex coordinates
        faces_l = gii_l.darrays[1].data    # face indices
        gii_r = nib.load(fsaverage5[right_key])
        coords_r = gii_r.darrays[0].data
        faces_r = gii_r.darrays[1].data

        n_l = coords_l.shape[0]  # 10242
        all_coords = np.vstack([coords_l, coords_r])  # (20484, 3)
        all_faces = np.vstack([faces_l, faces_r + n_l])  # (40960, 3)

        # Create trimesh with default gray vertex colors
        mesh = trimesh.Trimesh(vertices=all_coords, faces=all_faces)
        default_colors = np.full((len(all_coords), 4), [180, 180, 180, 255], dtype=np.uint8)
        mesh.visual = trimesh.visual.ColorVisuals(mesh=mesh, vertex_colors=default_colors)

        # Export GLB
        out_path = f"{OUTPUT_DIR}/fsaverage5_{surface_name}.glb"
        glb_data = mesh.export(file_type="glb")
        with open(out_path, "wb") as f:
            f.write(glb_data)

        print(f"  {surface_name}: {all_coords.shape[0]} vertices, {all_faces.shape[0]} faces → {out_path} ({len(glb_data)} bytes)")


def generate_atlas():
    """Generate atlas mapping: vertex index → region label."""
    from nilearn.datasets import fetch_atlas_surf_destrieux
    from nilearn import surface
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Fetching Destrieux atlas...")
    destrieux = fetch_atlas_surf_destrieux()

    labels = [l.decode() if isinstance(l, bytes) else str(l) for l in destrieux["labels"]]
    map_l = np.array(surface.load_surf_data(destrieux["map_left"])).astype(int)
    map_r = np.array(surface.load_surf_data(destrieux["map_right"])).astype(int)
    all_labels = np.concatenate([map_l, map_r])  # 20484 integers

    atlas = {
        "label_names": labels,
        "vertex_labels": all_labels.tolist(),
    }

    out_path = f"{OUTPUT_DIR}/brain_atlas.json"
    with open(out_path, "w") as f:
        json.dump(atlas, f)

    print(f"  Atlas: {len(labels)} regions, {len(all_labels)} vertex labels → {out_path}")


def generate_region_metadata():
    """Generate rich metadata for each brain region — what it does, what emotions, marketing relevance."""
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Map Destrieux atlas region names to functional descriptions
    # Destrieux uses anatomical naming — we map to cognitive/emotional function
    regions = {
        # ── FRONTAL LOBE ──
        "G_front_sup": {
            "display_name": "Superior Frontal Gyrus",
            "lobe": "Frontal",
            "function": "Executive function, planning, self-awareness",
            "emotions": ["confidence", "determination", "self-reflection"],
            "marketing": "Active when viewer is evaluating whether to take action. High activation = content is making them think about their own situation.",
            "tribe_meaning": "High → viewer is planning/deciding. Low → passive consumption.",
        },
        "G_front_middle": {
            "display_name": "Middle Frontal Gyrus",
            "lobe": "Frontal",
            "function": "Working memory, attention control, cognitive flexibility",
            "emotions": ["focus", "curiosity", "engagement"],
            "marketing": "Active when processing complex information. High = content is engaging working memory. Too high = content might be too complex.",
            "tribe_meaning": "High → mentally engaged. Very high → might be overwhelming.",
        },
        "G_front_inf-Opercular": {
            "display_name": "Broca's Area (Pars Opercularis)",
            "lobe": "Frontal",
            "function": "Speech production, language processing, syntax",
            "emotions": ["understanding", "comprehension"],
            "marketing": "Active when processing your message's language. High = your words are landing. Low = message isn't being processed.",
            "tribe_meaning": "High → message comprehended. Low → words not registering.",
        },
        "G_front_inf-Triangul": {
            "display_name": "Broca's Area (Pars Triangularis)",
            "lobe": "Frontal",
            "function": "Semantic processing, language comprehension",
            "emotions": ["understanding", "meaning-making"],
            "marketing": "Processing the meaning behind your words. High activation with a CTA = they understand what you're offering.",
            "tribe_meaning": "High → extracting meaning from content.",
        },
        "G_front_inf-Orbital": {
            "display_name": "Inferior Frontal (Orbital)",
            "lobe": "Frontal",
            "function": "Impulse control, decision inhibition, reward evaluation",
            "emotions": ["hesitation", "caution", "restraint"],
            "marketing": "The 'brake pedal' of the brain. High activation might mean viewer is resisting your CTA. You want this LOW when asking for action.",
            "tribe_meaning": "High → resisting action. Low → ready to act.",
        },
        "G_precentral": {
            "display_name": "Primary Motor Cortex",
            "lobe": "Frontal",
            "function": "Voluntary movement, action execution",
            "emotions": ["urge to act", "physical response", "readiness"],
            "marketing": "Active when viewer feels the urge to DO something — click, scroll, buy. The 'action impulse' signal.",
            "tribe_meaning": "High → they want to take action NOW.",
        },
        "S_precentral-sup-part": {
            "display_name": "Precentral Sulcus",
            "lobe": "Frontal",
            "function": "Motor planning, action preparation",
            "emotions": ["anticipation", "readiness"],
            "marketing": "Preparing to act. Pair with prefrontal activation for strongest conversion signal.",
            "tribe_meaning": "High → primed for action.",
        },
        "G_orbital": {
            "display_name": "Orbitofrontal Cortex",
            "lobe": "Frontal",
            "function": "Reward processing, value judgment, expected outcome",
            "emotions": ["desire", "anticipation", "reward expectation"],
            "marketing": "The 'is this worth it?' calculator. High activation = viewer perceives value. Critical for pricing pages and offers.",
            "tribe_meaning": "High → perceives value/reward. Low → not convinced.",
        },
        "G_rectus": {
            "display_name": "Gyrus Rectus",
            "lobe": "Frontal",
            "function": "Reward processing, emotional regulation",
            "emotions": ["pleasure", "satisfaction", "emotional balance"],
            "marketing": "Positive emotional response to content. High = content feels rewarding to watch.",
            "tribe_meaning": "High → enjoying the content.",
        },
        "G_and_S_cingul-Ant": {
            "display_name": "Anterior Cingulate Cortex",
            "lobe": "Frontal/Medial",
            "function": "Error detection, conflict monitoring, motivation",
            "emotions": ["frustration", "motivation", "conflict", "drive"],
            "marketing": "Fires when there's a gap between current state and desired state. Perfect for problem-agitation content. High = your problem statement is landing.",
            "tribe_meaning": "High → feeling the gap/pain point. Low → no tension.",
        },
        "G_and_S_cingul-Mid-Ant": {
            "display_name": "Mid-Anterior Cingulate",
            "lobe": "Frontal/Medial",
            "function": "Cognitive control, persistence, willpower",
            "emotions": ["determination", "persistence", "grit"],
            "marketing": "The 'I need to do something about this' signal. High activation during problem sections = they're motivated to solve it.",
            "tribe_meaning": "High → motivated to change.",
        },

        # ── TEMPORAL LOBE ──
        "G_temp_sup-Lateral": {
            "display_name": "Superior Temporal Gyrus",
            "lobe": "Temporal",
            "function": "Auditory processing, speech perception",
            "emotions": ["engagement with audio", "voice processing"],
            "marketing": "How well your audio/voiceover is landing. High = audio is engaging. Low = audio is being ignored or is absent.",
            "tribe_meaning": "High → audio channel is working. Low → visual/text carrying.",
        },
        "G_temp_sup-Plan_tempo": {
            "display_name": "Planum Temporale",
            "lobe": "Temporal",
            "function": "Auditory language processing, music perception",
            "emotions": ["rhythm", "musicality", "auditory pleasure"],
            "marketing": "Responds to music and rhythm in your content. High = your music/sound design is effective.",
            "tribe_meaning": "High → audio/music is adding value.",
        },
        "G_temporal_middle": {
            "display_name": "Middle Temporal Gyrus",
            "lobe": "Temporal",
            "function": "Semantic memory, language comprehension, meaning",
            "emotions": ["recognition", "familiarity", "understanding"],
            "marketing": "Processing meaning and connecting to existing knowledge. High = content connects to what they already know/believe.",
            "tribe_meaning": "High → connecting to existing beliefs.",
        },
        "G_temporal_inf": {
            "display_name": "Inferior Temporal Gyrus",
            "lobe": "Temporal",
            "function": "Object recognition, visual categorization",
            "emotions": ["recognition", "categorization"],
            "marketing": "Recognizing and categorizing what they see. High during product shots = they're processing your product.",
            "tribe_meaning": "High → recognizing/categorizing visual content.",
        },
        "G_temp_sup-G_T_transv": {
            "display_name": "Heschl's Gyrus (Primary Auditory)",
            "lobe": "Temporal",
            "function": "Primary auditory cortex, sound processing",
            "emotions": ["alertness", "auditory attention"],
            "marketing": "Raw sound processing. High = something in the audio grabbed attention (voice change, sound effect, music drop).",
            "tribe_meaning": "Spike → audio pattern interrupt detected.",
        },

        # ── PARIETAL LOBE ──
        "G_postcentral": {
            "display_name": "Primary Somatosensory Cortex",
            "lobe": "Parietal",
            "function": "Touch, body awareness, physical sensation",
            "emotions": ["physical empathy", "embodied response"],
            "marketing": "Active during physical demonstrations. If showing a product being used/touched, this fires.",
            "tribe_meaning": "High → feeling physical empathy with content.",
        },
        "G_parietal_sup": {
            "display_name": "Superior Parietal Lobule",
            "lobe": "Parietal",
            "function": "Spatial attention, visuomotor coordination",
            "emotions": ["spatial awareness", "visual tracking"],
            "marketing": "Following movement on screen. High during demos/tutorials = they're tracking what you're showing.",
            "tribe_meaning": "High → visually tracking content closely.",
        },
        "G_pariet_inf-Supramar": {
            "display_name": "Supramarginal Gyrus",
            "lobe": "Parietal",
            "function": "Empathy, emotional processing of language, phonological processing",
            "emotions": ["empathy", "emotional language processing"],
            "marketing": "Empathy circuit. High during testimonials or emotional stories = they're feeling what the speaker feels.",
            "tribe_meaning": "High → empathizing with speaker/character.",
        },
        "G_pariet_inf-Angular": {
            "display_name": "Angular Gyrus",
            "lobe": "Parietal",
            "function": "Semantic integration, reading, number processing",
            "emotions": ["comprehension", "integration", "aha moment"],
            "marketing": "The 'aha moment' region. High = pieces are clicking together. Active when your argument makes sense.",
            "tribe_meaning": "High → understanding clicks into place.",
        },
        "G_precuneus": {
            "display_name": "Precuneus",
            "lobe": "Parietal/Medial",
            "function": "Self-referential thinking, autobiographical memory, imagination",
            "emotions": ["self-reflection", "imagination", "nostalgia", "aspiration"],
            "marketing": "The 'imagine yourself' region. High during future-pacing, aspirational content, before/after. Critical for 'picture your life after using this' messaging.",
            "tribe_meaning": "High → imagining themselves in the scenario.",
        },

        # ── OCCIPITAL LOBE ──
        "G_occipital_sup": {
            "display_name": "Superior Occipital Gyrus",
            "lobe": "Occipital",
            "function": "Visual processing, peripheral vision",
            "emotions": ["visual alertness"],
            "marketing": "Basic visual processing. High = visuals are being processed. Low = visual fatigue or boring imagery.",
            "tribe_meaning": "High → eyes are engaged.",
        },
        "G_occipital_middle": {
            "display_name": "Middle Occipital Gyrus",
            "lobe": "Occipital",
            "function": "Object recognition, motion detection",
            "emotions": ["visual interest", "motion tracking"],
            "marketing": "Tracking movement and recognizing objects. Scene changes and motion graphics spike this.",
            "tribe_meaning": "Spike → visual change detected.",
        },
        "G_oc-temp_lat-fusifor": {
            "display_name": "Fusiform Face Area",
            "lobe": "Temporal/Occipital",
            "function": "Face recognition, person identification, social processing",
            "emotions": ["social connection", "trust", "familiarity", "tribal belonging"],
            "marketing": "THE most important region for social media content. Faces in content trigger immediate engagement. No face = this stays silent. A face looking at camera = maximum activation.",
            "tribe_meaning": "High → face detected, social brain activated. Zero → no human face.",
        },
        "Pole_occipital": {
            "display_name": "Occipital Pole (V1)",
            "lobe": "Occipital",
            "function": "Primary visual cortex, basic visual features (edges, contrast, color)",
            "emotions": ["visual stimulation"],
            "marketing": "Raw visual processing. High contrast, bright colors, sharp edges spike this. Flat/muted visuals don't.",
            "tribe_meaning": "High → visually stimulating. Low → visually flat.",
        },
        "S_calcarine": {
            "display_name": "Calcarine Sulcus (V1/V2)",
            "lobe": "Occipital",
            "function": "Central visual field processing",
            "emotions": ["focused attention"],
            "marketing": "What's in the center of the screen. If this is high, the viewer is focused on the main subject.",
            "tribe_meaning": "High → looking at the center of frame.",
        },

        # ── INSULAR / LIMBIC ──
        "G_Ins_lg_and_S_cent_ins": {
            "display_name": "Insula (Long Gyri)",
            "lobe": "Insular",
            "function": "Interoception, gut feeling, disgust, empathy, risk perception",
            "emotions": ["gut feeling", "disgust", "trust", "empathy", "risk aversion"],
            "marketing": "The 'gut reaction' center. High = visceral emotional response. This is where 'this feels right' or 'something feels off' lives. Critical for building trust.",
            "tribe_meaning": "High → strong gut/emotional reaction. Context determines positive or negative.",
        },
        "G_cingul-Post-dorsal": {
            "display_name": "Posterior Cingulate Cortex",
            "lobe": "Limbic/Medial",
            "function": "Default mode network hub, self-referential thinking, autobiographical memory",
            "emotions": ["self-relevance", "personal connection", "nostalgia", "belonging"],
            "marketing": "THE default mode network hub. High = content feels personally relevant. 'You' language, personal stories, 'people like you' framing activates this. The TRIBE goldmine for emotional content.",
            "tribe_meaning": "High → personally relevant. Low → impersonal/generic.",
        },
        "G_cingul-Post-ventral": {
            "display_name": "Ventral Posterior Cingulate",
            "lobe": "Limbic/Medial",
            "function": "Emotional processing, memory retrieval",
            "emotions": ["emotional memory", "sentimentality"],
            "marketing": "Recalling emotional memories. High during nostalgic or aspirational content.",
            "tribe_meaning": "High → triggering emotional memories.",
        },

        # ── OTHER ──
        "G_oc-temp_med-Parahip": {
            "display_name": "Parahippocampal Gyrus",
            "lobe": "Temporal/Medial",
            "function": "Scene recognition, spatial memory, context processing",
            "emotions": ["familiarity", "place recognition", "context"],
            "marketing": "Recognizing scenes and environments. High during location shots, office tours, lifestyle footage.",
            "tribe_meaning": "High → processing the scene/environment.",
        },
        "Pole_temporal": {
            "display_name": "Temporal Pole",
            "lobe": "Temporal",
            "function": "Social cognition, theory of mind, name/face association",
            "emotions": ["social understanding", "mentalizing", "perspective-taking"],
            "marketing": "Understanding other people's perspectives. High during testimonials = viewer is understanding the speaker's experience. Critical for social proof.",
            "tribe_meaning": "High → understanding another person's perspective.",
        },
        "S_temporal_sup": {
            "display_name": "Superior Temporal Sulcus",
            "lobe": "Temporal",
            "function": "Biological motion, social perception, voice processing",
            "emotions": ["social awareness", "voice identity"],
            "marketing": "Detects human movement and voice identity. High = viewer recognizes this as a real person speaking (not AI/generic).",
            "tribe_meaning": "High → perceiving authentic human communication.",
        },
    }

    # Add catch-all for regions not explicitly mapped
    default_entry = {
        "display_name": "Unknown Region",
        "lobe": "Unknown",
        "function": "Not yet mapped to specific cognitive function",
        "emotions": [],
        "marketing": "Activation detected but functional mapping not yet established for this region.",
        "tribe_meaning": "Requires further analysis to determine marketing significance.",
    }

    out_path = f"{OUTPUT_DIR}/brain_regions.json"
    output = {"regions": regions, "default": default_entry}
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"  Region metadata: {len(regions)} regions mapped → {out_path}")


if __name__ == "__main__":
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=== TRIBE Brain Asset Generator ===\n")

    print("Step 1: Generating mesh files...")
    generate_meshes()

    print("\nStep 2: Generating atlas mapping...")
    generate_atlas()

    print("\nStep 3: Generating region metadata...")
    generate_region_metadata()

    print(f"\nDone! Assets in ./{OUTPUT_DIR}/")
    print("Copy to your Next.js app: cp -r brain_assets/* /path/to/app/public/brain/")
