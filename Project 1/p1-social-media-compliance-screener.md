# Social Media Post Compliance Screener

## Objective

Develop a pre-publish compliance backend for a marketing team managing
several brand accounts, where a scheduled post needs a second set of eyes
before it goes live — not to approve every post by hand, but to catch the
two things that actually cause damage: a caption that accidentally
includes a customer's personal information (copy-pasted from a support
reply into a "look how happy our customers are" post), or a caption whose
tone reads far more negative than the brand ever intends to sound.
The system should make it easy to manage brands and schedule posts, and
automatically gate every post behind a compliance check via **Amazon
Comprehend** — screening for personal information and off-tone sentiment —
before it's allowed to move from `pending` to `approved`. Most posts carry
an image alongside the caption, and the image needs the same gate: **Amazon
Rekognition** screens any attached photo for inappropriate content before
a post can be approved, since a caption can pass every text check while
its image is the actual problem. Prioritize correctness on the data
layer — a post's compliance status is an explicit state machine driven by
evidence (which check failed and why), never a silent pass-through. The
deliverable is a containerized service that runs locally via
`docker compose up` and exposes a documented REST API, backed by a real
PostgreSQL database and real (in production) calls to two AWS managed AI
services.

## Functional Requirements

### Brand Management

- **Add New Brand:**
  - Marketing admins should be able to register a new brand by specifying
    its name and industry.
- **View Brands:**
  - Provide a dashboard endpoint listing all brands with their core
    metadata and post count broken down by compliance status.
- **Edit Brand:**
  - Allow updating a brand's name or industry.
- **Delete Brand:**
  - Implement deletion with a confirmation requirement (such as requiring
    the brand id in the request body). Decide (and document in your
    README) whether deleting a brand cascades to delete its posts.

### Post Management

- **Schedule Post:**
  - Marketers should be able to submit a post for a brand by specifying
    the platform (`Literal["twitter", "instagram", "facebook",
    "linkedin"]`), caption text, an optional image, and a scheduled
    publish time. New posts default to `compliance_status: pending`.
- **Attach Post Image:**
  - Accept an optional `multipart/form-data` upload (JPG or PNG) alongside
    a post. Store the raw image in S3 — a post with no image is valid and
    skips image screening entirely.
- **View Posts:**
  - List all posts for a brand, including compliance status and any
    flagged reasons, with filter support by platform and compliance status.
- **Review Post:**
  - Allow a human reviewer to move a post from `pending` to `approved` or
    `blocked`, including overriding an AI-driven block after manual
    review (with the override reason recorded).
- **Delete Post:**
  - Implement deletion with a confirmation requirement (such as requiring
    the post id in the request body).

### API Design & Developer Experience

- **Consistent Error Envelopes:**
  - All errors (validation, not-found, conflict, upstream AI-service
    failure) should return a consistent JSON shape with an error code,
    human-readable message, and request_id.
- **Liveness and Readiness:**
  - Expose `/live` and `/ready` endpoints. `/live` confirms the process is
    up; `/ready` confirms downstream dependencies (the database) are
    reachable. Comprehend/Rekognition reachability is *not* part of
    `/ready` — see Edge Case Handling below.
- **Structured Request Logging:**
  - Every request should emit a structured log line containing method,
    path, status code, duration, and correlation id, as machine-parseable JSON.
- **Filtered Listings:**
  - List endpoints should support filter + sort query parameters across
    `platform`, `compliance_status`, and scheduled date.

### Edge Case Handling

- **Comprehend Is Unavailable:**
  - Decide how post submission behaves if PII or sentiment screening
    fails. Given that this is a pre-publish safety gate, a post should
    **never** be auto-approved when screening couldn't run — decide
    whether it stays `pending` indefinitely (requiring manual review) or
    is retried automatically, and document your choice.
- **PII Detected in a Caption:**
  - A post with detected PII must never move directly to `approved` —
    decide whether it's auto-set to `blocked` with the detected span(s)
    recorded as the reason, requiring the marketer to edit the caption
    and resubmit. Document your choice.
- **Sentiment Reads More Negative Than Intended:**
  - A post that scores strongly `NEGATIVE` should be flagged for human
    review rather than auto-blocked outright (tone is more subjective
    than PII) — decide your exact threshold and document it.
- **Very Short Caption:**
  - Comprehend requires non-empty input and behaves unpredictably on
    single-character/emoji-only text. Decide on (and enforce via
    Pydantic) a minimum caption length, and document why you picked it.
- **Rekognition Is Unavailable, or the Image Upload Is Malformed:**
  - Decide how a post with an attached image behaves if moderation
    screening fails — the same "never auto-approve when screening
    couldn't run" rule from PII/sentiment screening applies here too.
    Reject non-JPG/PNG uploads with a 422 naming accepted formats, and
    enforce a maximum file size.
- **Image Flagged, Caption Clean (or Vice Versa):**
  - A post is blocked if *either* the caption or the image fails its
    respective check — decide how the blocked reason communicates which
    one failed (or both), since the marketer needs to know what to fix
    before resubmitting.
- **Concurrent Mutations:**
  - Describe what happens if two reviewers try to approve/block the same
    post at the same time, or a post is edited while it's mid-screening.
    Document the expected behavior.

### AI-Assisted Feature (Required)

> **Sequencing — build this last.** This feature is a required, graded
> part of the deliverable, not an optional stretch goal. Implement it only
> after the core CRUD service is complete and working end to end — the AI
> pipeline should be layered on top of a finished functional deliverable,
> not built in parallel with it. A complete core with the AI feature added
> last scores well; an AI pipeline bolted onto an incomplete or broken core
> does not.

- **PII Screening:**
  - When a post is submitted, call Comprehend's `DetectPiiEntities`
    against the caption text. If anything is found, auto-set
    `compliance_status` to `blocked` (per your Edge Case Handling decision
    above) with the detected entity type recorded as the reason — never
    silently ignored.
- **Tone Screening:**
  - Call Comprehend's `DetectSentiment` against the same caption. If it
    reads strongly `NEGATIVE`, flag the post for mandatory human review
    rather than letting it auto-approve.
- **Pending-Review Queue:**
  - Add `GET /brands/{id}/posts/pending-review` returning every post
    still awaiting a human decision (blocked by PII, flagged for tone, or
    simply not yet reviewed) — the actual pre-publish compliance gate
    payoff from the Objective, not a status field nobody checks before
    a post goes out.
- **Image Moderation:**
  - When a post has an attached image, call Rekognition's
    `DetectModerationLabels` against the stored image. If any label is
    returned, block the post (per your Edge Case Handling decision above)
    with the moderation label recorded as the reason — the same
    evidence-backed blocking discipline as the text checks, applied to
    the image.
- **Isolated, Mockable AWS Clients:**
  - The Comprehend and Rekognition calls (and S3 storage) must each go
    through their own single, injectable client module (mirroring the
    shared-session pattern from this course's Week 3 boto3 material) so
    your test suite can substitute fake/mocked clients and run without
    live AWS credentials.

## Stretch Goals

Stretch goals are features you want to add to an application, but they
aren't required. For this project, Stretch Goals are a way to go above and
beyond the minimum requirements and I look forward to seeing what unique
features you will add to your project. Here are some examples you might consider:

- **Deploy the App to AWS:**
  - Push your Docker image to Amazon ECR and run the stack on an AWS
    compute service of your choice (App Runner, ECS, or an EC2 instance).
    Document your deployment architecture and any cost/cleanup considerations.
- **Bedrock-Powered Rewrite Suggestions:**
  - Add an endpoint that sends a flagged post to a foundation model via
    Bedrock's Converse API and returns a suggested rewrite that removes
    the flagged issue while preserving intent. This uses content not yet
    covered in lecture at the time this project is assigned — a good
    stretch goal for anyone who wants to explore ahead.
- **SageMaker Custom Model:**
  - Train a simple custom model that predicts brand-voice fit on a
    continuous scale from caption features, hosted behind a SageMaker
    endpoint, instead of a binary sentiment threshold. Also beyond the
    current curriculum — a good "go deeper" option.
- **Rate Limiting:**
  - Add Flask-Limiter to throttle post submissions per client IP. Choose
    a sensible limit and document why in your README.
- **Second Entity Relationship:**
  - Extend the model to support a `Reviewer` entity — the specific staff
    member who approved/blocked each post, with a review history per reviewer.
- **Minimal Web UI:**
  - Add a single HTML page (or React app) that consumes your API and
    displays the pending-review queue with one-click approve/block actions.
- **Persistent Audit Log:**
  - Record every mutation (create / update / delete / review decision)
    into an audit table with timestamp, action, entity, and actor.
- **Bulk Import:**
  - Add an endpoint that accepts a CSV of a week's scheduled posts (e.g.,
    exported from a content calendar tool) and screens them all in one
    transaction, with all-or-nothing semantics.
- **Per-Brand Custom Sensitivity:**
  - Allow each brand to configure its own sentiment threshold for
    tone-flagging, since a comedy-focused brand's acceptable tone range
    differs from a healthcare brand's.

## Technical Requirements

Must be a backend solution consisting of:

- Python 3.11+
- Flask 3.x with the app-factory pattern and blueprints
- Pydantic v2 for HTTP-boundary validation
- PostgreSQL via SQLAlchemy 2.0 and Flask-Migrate, with a real migration
  history checked into the repo (no `create_all()` in production code paths)
- boto3, authenticated via a dedicated, least-privilege IAM user (never
  root/admin credentials) — the IAM policy JSON granting only
  `comprehend:DetectPiiEntities`, `comprehend:DetectSentiment`,
  `rekognition:DetectModerationLabels`, and `s3:PutObject`/`s3:GetObject`
  (scoped to your bucket) must be committed to the repo
- Separate, injectable client wrapper modules for Comprehend, Rekognition,
  and S3 — not `boto3.client(...)` called ad hoc from route handlers
- structlog for structured JSON logging with per-request correlation IDs
- pytest with fixtures and parametrize for the test suite; AWS calls must
  be mocked/stubbed in tests (e.g. `unittest.mock` or `botocore.stub.Stubber`)
  so the suite runs without live AWS credentials or network access
- Docker multi-stage Dockerfile + docker-compose.yml for a local
  api + db stack, with a database health check gating the API's startup
- pyproject.toml with a src/ layout and a `[project.optional-dependencies]` dev block
- Code should be available in a private GitHub repository, with the
  instructor added as a collaborator
- Possesses all required CRUD functionality
- Handles edge cases effectively

## Non-Functional Requirements

- Well-documented code (module docstrings + function docstrings on public surfaces)
- Code upholds industry best practices (SOLID / DRY / single-responsibility)
- Type hints on every function signature
- Test coverage on happy + error paths (at least 15 pytest tests, including
  at least one test per Comprehend- and Rekognition-backed endpoint using
  mocked clients)
- Structured logs (no print statements in production code paths)
- Container runnable via a single `docker compose up`
- README with one-line install and one-line run instructions, plus your
  documented decisions for every Edge Case Handling item above
- Pydantic models have explicit field constraints (Literal types, min/max
  length on caption text)
- No mutable default arguments; use `field(default_factory=...)` for collections
- Errors raise typed exceptions from a DomainError hierarchy, not generic Exception
- Data model documented as an entity-relationship diagram (ERD) — every
  entity, its fields, and the cardinality of each relationship — checked
  into the repository
- A kanban board with a complete, prioritized backlog is set up **before
  development begins**; work is pulled from the board rather than started ad hoc
