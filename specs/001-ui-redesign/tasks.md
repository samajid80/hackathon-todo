# Tasks: Modern UI Redesign and Authentication State Handling

**Input**: Design documents from `/specs/001-ui-redesign/`
**Prerequisites**: plan.md (tech stack, structure), spec.md (user stories), research.md (design decisions)

**Tests**: Not requested in specification - manual testing via quickstart.md scenarios

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend-only feature**: All paths under `frontend/` directory
- Components: `frontend/components/`
- Pages: `frontend/app/`
- Utilities: `frontend/lib/`
- Styles: `frontend/styles/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and directory structure for new components

- [X] T001 Create directory structure for landing components at frontend/components/landing/
- [X] T002 Create directory structure for custom hooks at frontend/lib/hooks/
- [X] T003 [P] Verify existing Better-Auth integration in frontend/lib/auth-client.ts
- [X] T004 [P] Review existing Tailwind configuration in frontend/tailwind.config.js

**Checkpoint**: ✅ Directory structure ready for component development

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core authentication hook that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Create useAuth custom hook at frontend/lib/hooks/useAuth.ts with Better-Auth useSession() integration
- [X] T006 Add TypeScript interface for auth hook return type (user, isAuthenticated, isLoading) in frontend/lib/hooks/useAuth.ts
- [X] T007 Test useAuth hook manually by importing in a test component to verify session detection works

**Checkpoint**: ✅ Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - First-Time Visitor Landing Experience (Priority: P1) 🎯 MVP

**Goal**: Unauthenticated users see a modern, professional landing page with feature highlights and clear CTAs

**Independent Test**: Visit homepage as unauthenticated user (clear cookies), verify feature highlights displayed, Sign In/Create Account buttons visible, modern design applied

### Implementation for User Story 1

- [X] T008 [P] [US1] Create FeatureCard component at frontend/components/landing/FeatureCard.tsx with icon, title, description props
- [X] T009 [P] [US1] Create FeatureGrid component at frontend/components/landing/FeatureGrid.tsx to display 3 feature cards
- [X] T010 [P] [US1] Create LandingHero component at frontend/components/landing/LandingHero.tsx with headline, subheadline, and CTA buttons
- [X] T011 [US1] Add design system tokens to frontend/styles/globals.css for gradients, improved typography scale, and spacing
- [X] T012 [US1] Create UnauthenticatedView component in frontend/app/page.tsx that renders LandingHero and FeatureGrid
- [X] T013 [US1] Define feature content data (3 features: Task Management, Filter & Sort, Secure & Private) in frontend/app/page.tsx
- [X] T014 [US1] Add responsive styling to LandingHero for mobile (320px), tablet (768px), desktop (1024px+) breakpoints
- [X] T015 [US1] Add smooth fade-in animation to UnauthenticatedView using Tailwind animate utilities
- [X] T016 [US1] Test responsive design at 320px, 768px, 1024px, 1920px widths using browser DevTools

**Checkpoint**: ✅ User Story 1 is fully functional and testable independently - unauthenticated landing page complete

---

## Phase 4: User Story 2 - Authenticated User Homepage Navigation (Priority: P1)

**Goal**: Authenticated users see "Go to Tasks" button instead of Sign In/Create Account, with user identification displayed

**Independent Test**: Log in to application, navigate to homepage, verify "Go to Tasks" button shown, Sign In/Create Account hidden, user email/name displayed, logout option visible

### Implementation for User Story 2

- [X] T017 [P] [US2] Create AuthenticatedView component in frontend/app/page.tsx with "Go to Tasks" button and welcome message
- [X] T018 [P] [US2] Create LoadingSkeleton component in frontend/app/page.tsx for auth state loading state
- [X] T019 [US2] Update Navbar component at frontend/components/Navbar.tsx to display user email/name for authenticated users
- [X] T020 [US2] Add logout button to Navbar component at frontend/components/Navbar.tsx using Better-Auth signOut function
- [X] T021 [US2] Implement conditional rendering in frontend/app/page.tsx using useAuth hook (show LoadingSkeleton while loading, AuthenticatedView if authenticated, UnauthenticatedView if not)
- [X] T022 [US2] Add "use client" directive to frontend/app/page.tsx to enable client-side auth detection
- [X] T023 [US2] Add Link to /tasks page in AuthenticatedView "Go to Tasks" button
- [X] T024 [US2] Test auth state detection by logging in/out and verifying UI updates correctly
- [X] T025 [US2] Verify no flash of unauthenticated content (FOUC) when page loads for authenticated users

**Checkpoint**: ✅ User Stories 1 AND 2 both work independently - auth state detection complete

---

## Phase 5: User Story 3 - Professional Visual Design (Priority: P2)

**Goal**: Apply modern, professional, sleek visual design across landing page with consistent design language and responsive layout

**Independent Test**: Review landing page visually on desktop/tablet/mobile, verify modern typography (3xl-5xl headlines), consistent spacing (Tailwind scale), gradient backgrounds, smooth transitions, professional appearance

### Implementation for User Story 3

- [X] T026 [P] [US3] Add gradient background to landing page hero section using Tailwind bg-gradient-to-r from-blue-50 to-indigo-50
- [X] T027 [P] [US3] Update typography scale in LandingHero to use text-4xl md:text-5xl lg:text-6xl for headline
- [X] T028 [P] [US3] Add card shadows and hover effects to FeatureCard component using shadow-sm hover:shadow-md transition
- [X] T029 [P] [US3] Update color palette in FeatureCard icons to use text-blue-600 (primary) and text-indigo-600 (secondary)
- [X] T030 [US3] Add smooth transition classes (transition-all duration-300) to all interactive elements (buttons, cards)
- [X] T031 [US3] Update button styling in LandingHero with rounded-md, hover states, and focus ring styles
- [X] T032 [US3] Add consistent spacing using Tailwind spacing scale (py-12 md:py-16 lg:py-20) to sections
- [X] T033 [US3] Ensure visual hierarchy with font weights (font-bold for headlines, font-semibold for subheadings)
- [X] T034 [US3] Add accessible color contrast ratios (WCAG AA) for all text on backgrounds
- [X] T035 [US3] Test visual design on multiple browsers (Chrome, Firefox, Safari, Edge) for consistency
- [X] T036 [US3] Verify responsive layout from 320px to 2560px screen widths

**Checkpoint**: ✅ All user stories are independently functional - professional visual design complete

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements that affect the overall landing page experience

- [X] T037 [P] Add meta tags for SEO in frontend/app/layout.tsx (title, description, Open Graph)
- [X] T038 [P] Optimize loading performance by ensuring auth check completes in under 100ms
- [X] T039 [P] Add aria-labels to interactive elements for accessibility (buttons, links)
- [X] T040 [P] Verify keyboard navigation works correctly (Tab through all interactive elements)
- [X] T041 Add error boundary to handle auth check failures gracefully in frontend/app/page.tsx
- [ ] T042 Test all edge cases from spec.md (session expiry, network error, mobile screens)
- [ ] T043 Run all quickstart.md validation scenarios (7 test scenarios)
- [ ] T044 Verify Core Web Vitals targets met (LCP < 2.5s, FID < 100ms, CLS < 0.1)
- [ ] T045 [P] Update documentation with component usage examples in feature README
- [ ] T046 Create visual regression test baseline screenshots for future comparison

**Checkpoint**: Feature complete and ready for production

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P1 → P2)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Requires US1 components as base but modifies different concerns
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Enhances US1 and US2 visually but doesn't block them

### Within Each User Story

- Components before page integration
- Core components before composite components
- Styling after component structure
- Testing after implementation
- Story complete before moving to next priority

### Parallel Opportunities

#### Phase 1: Setup (4 parallel tasks)
```bash
# All setup tasks can run in parallel:
T001 Create landing components directory
T002 Create hooks directory
T003 [P] Verify Better-Auth integration
T004 [P] Review Tailwind configuration
```

#### Phase 2: Foundational (Limited parallelism)
```bash
# T005 must complete first, then T006-T007 can be parallel
T005 Create useAuth hook
T006 [P] Add TypeScript interfaces
T007 [P] Test hook manually
```

#### Phase 3: User Story 1 (3 parallel components at start)
```bash
# Launch all base components together:
T008 [P] [US1] Create FeatureCard component
T009 [P] [US1] Create FeatureGrid component
T010 [P] [US1] Create LandingHero component

# Then sequential integration:
T011-T016 in order
```

#### Phase 4: User Story 2 (2 parallel components at start)
```bash
# Launch view components together:
T017 [P] [US2] Create AuthenticatedView
T018 [P] [US2] Create LoadingSkeleton

# Then integrate:
T019-T025 in order
```

#### Phase 5: User Story 3 (5 parallel styling tasks)
```bash
# Visual design improvements can mostly run in parallel:
T026 [P] [US3] Add gradient backgrounds
T027 [P] [US3] Update typography scale
T028 [P] [US3] Add card shadows/hover
T029 [P] [US3] Update color palette
T030 [P] [US3] Add transitions
```

#### Phase 6: Polish (Most tasks parallel)
```bash
# Many polish tasks are independent:
T037 [P] Add SEO meta tags
T038 [P] Optimize performance
T039 [P] Add aria-labels
T040 [P] Verify keyboard navigation
T045 [P] Update documentation
```

---

## Parallel Example: User Story 1

```bash
# Launch all base components for User Story 1 together:
Task: "Create FeatureCard component at frontend/components/landing/FeatureCard.tsx"
Task: "Create FeatureGrid component at frontend/components/landing/FeatureGrid.tsx"
Task: "Create LandingHero component at frontend/components/landing/LandingHero.tsx"

# These three tasks work on different files with no dependencies
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2)

1. Complete Phase 1: Setup (4 tasks)
2. Complete Phase 2: Foundational (3 tasks - CRITICAL)
3. Complete Phase 3: User Story 1 (9 tasks)
4. **STOP and VALIDATE**: Test unauthenticated landing page independently
5. Complete Phase 4: User Story 2 (9 tasks)
6. **STOP and VALIDATE**: Test authenticated navigation independently
7. Deploy/demo if ready (MVP covers both P1 user stories)

### Incremental Delivery

1. Complete Setup + Foundational → Auth hook ready (7 tasks)
2. Add User Story 1 → Test independently → Unauthenticated landing page complete (9 tasks)
3. Add User Story 2 → Test independently → Auth state handling complete (9 tasks)
4. Add User Story 3 → Test independently → Visual design polish complete (11 tasks)
5. Add Polish phase → Final validation → Production ready (10 tasks)

Total: 46 tasks across 6 phases

### Parallel Team Strategy

With multiple developers (after Foundational phase completes):

1. Team completes Setup (Phase 1) together - 4 tasks
2. Team completes Foundational (Phase 2) together - 3 tasks (BLOCKS all stories)
3. Once Foundational is done:
   - Developer A: User Story 1 (unauthenticated landing) - 9 tasks
   - Developer B: User Story 2 (authenticated navigation) - 9 tasks
   - Developer C: User Story 3 (visual design) - 11 tasks
4. Stories complete and integrate independently
5. Team collaborates on Polish phase - 10 tasks

---

## Task Summary

| Phase | Tasks | Parallel | User Story | Priority |
|-------|-------|----------|------------|----------|
| Phase 1: Setup | 4 | 4 | N/A | Foundation |
| Phase 2: Foundational | 3 | 2 | N/A | Foundation |
| Phase 3: User Story 1 | 9 | 3 | US1 | P1 (MVP) |
| Phase 4: User Story 2 | 9 | 2 | US2 | P1 (MVP) |
| Phase 5: User Story 3 | 11 | 5 | US3 | P2 |
| Phase 6: Polish | 10 | 5 | N/A | Final |
| **Total** | **46** | **21** | **3 stories** | - |

**Parallel Opportunities**: 21 tasks (46% of total) can run in parallel with other tasks in their phase

**MVP Scope**: Phases 1-4 (25 tasks) deliver both P1 user stories

**Full Feature**: All 46 tasks deliver complete feature with professional design and polish

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- No tests generated (not requested in spec - use quickstart.md for manual testing)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Frontend-only feature - no backend or database changes required
