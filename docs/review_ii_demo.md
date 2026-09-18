# NeuroTrack AI — Review-II Step-by-Step Presentation & Demo Walkthrough

## Step-by-Step Live Demo Instructions

1. **Launch Services**:
   - Run `docker compose up --build` or launch backend (`uvicorn app.main:app --port 8000`) and frontend (`npm run dev`).
   - Open dashboard at `http://localhost:3000`.

2. **Verify System Health**:
   - Point out the top-right green system status badge showing `BACKEND: HEALTHY`.

3. **Select/Register Demo Child Profile**:
   - Navigate to **Children** tab.
   - Click **Add Child Profile** and enter `External ID: C-1042`, `Age: 36`, `Gender: Male`. Click **Save Child Record**.

4. **Create Joint Attention Session**:
   - Navigate to **New Session** tab.
   - Select child `C-1042` and task `Standardized Joint Attention Task`. Click **Proceed to Video Upload**.

5. **Upload & Analyze Sample Recording**:
   - Drag and drop a sample MP4 video recording.
   - Click **Upload & Execute Pipeline**.
   - Watch the live execution status as the backend validates the file, samples frames, runs MediaPipe Face & Pose CV, and calculates feature metrics.

6. **Inspect Structured Behavioral Report**:
   - **Quality Gate Card**: Show overall quality score, blur score (variance of Laplacian), face/pose landmark visibility ratios, and decision (`VALID` vs `REASSESSMENT_REQUIRED`).
   - **Computed Behavioral Metrics**: Show live calculated values for `target_orientation_ratio`, `orientation_latency_sec`, `fixation_duration_sec`, and `gaze_shift_count`.
   - **Extracted Feature Dictionary Table**: Explain units, validity flags, and confidence scores.
   - **Annotated CV Evidence Gallery**: Click thumbnail snapshots to display MediaPipe face mesh and body skeleton keypoint overlays generated live by OpenCV.

7. **Demonstrate Quality Gate Rejection (Optional)**:
   - Repeat upload with a blurry or pitch-black video clip to demonstrate that the Quality Gate correctly marks status as `REASSESSMENT_REQUIRED` with transparent reasons.
