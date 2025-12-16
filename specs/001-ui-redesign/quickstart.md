# Quickstart: Modern UI Redesign and Authentication State Handling

**Feature**: 001-ui-redesign | **Date**: 2025-12-16
**Purpose**: Quick testing guide and acceptance validation scenarios

## Prerequisites

Before testing this feature, ensure:

1. ✅ Frontend development server is running (`cd frontend && npm run dev`)
2. ✅ Better-Auth is configured (`frontend/.env.local` has required variables)
3. ✅ Backend API is running (for authentication) (`cd backend && uvicorn backend.main:app --reload`)
4. ✅ Database is accessible (Neon PostgreSQL connection)

## Quick Start Commands

```bash
# Terminal 1: Start backend
cd backend
source .venv/bin/activate  # or activate your venv
uvicorn backend.main:app --reload --port 8000

# Terminal 2: Start frontend
cd frontend
npm run dev

# Access application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Test Scenarios

### Scenario 1: Unauthenticated User Landing Page (P1)

**User Story**: First-Time Visitor Landing Experience

**Steps**:
1. Clear browser cookies/session storage
2. Navigate to `http://localhost:3000`
3. Observe the landing page

**Expected Outcomes**:
- ✅ Modern, professional hero section is displayed
- ✅ Headline clearly communicates application purpose
- ✅ "Sign In" button is visible
- ✅ "Create Account" button is visible
- ✅ At least 3 feature highlight cards are displayed
- ✅ Feature descriptions are clear and benefit-focused
- ✅ Visual design is modern (gradients, spacing, typography)
- ✅ No loading flash or content shift
- ✅ Page loads in under 1 second

**Acceptance Criteria**:
- FR-001: Feature highlights visible ✓
- FR-008: Modern professional styling applied ✓
- FR-010: Responsive on desktop/tablet/mobile ✓
- SC-002: Users can identify 3+ features within 10 seconds ✓

---

### Scenario 2: Authenticated User Landing Page (P1)

**User Story**: Authenticated User Homepage Navigation

**Steps**:
1. Log in to the application (`http://localhost:3000/login`)
2. Enter valid credentials
3. After login, navigate back to `http://localhost:3000`
4. Observe the landing page

**Expected Outcomes**:
- ✅ "Sign In" button is NOT displayed
- ✅ "Create Account" button is NOT displayed
- ✅ "Go to Tasks" or "View My Tasks" button IS displayed
- ✅ User email or username is displayed in navigation
- ✅ Logout option is accessible
- ✅ No flash of unauthenticated content during page load
- ✅ Authentication state resolves in under 1 second

**Acceptance Criteria**:
- FR-002: User authentication status detected ✓
- FR-003: Sign In/Create Account hidden for authenticated users ✓
- FR-004: "Go to Tasks" button displayed ✓
- FR-006: User identification displayed ✓
- FR-007: Logout option accessible ✓
- SC-001: Appropriate navigation within 1 second ✓
- SC-005: Zero user confusion ✓

---

### Scenario 3: Navigation from Landing to Tasks (P1)

**User Story**: Authenticated User Homepage Navigation

**Steps**:
1. As an authenticated user on `http://localhost:3000`
2. Click the "Go to Tasks" button
3. Observe navigation

**Expected Outcomes**:
- ✅ User is navigated to `/tasks` page
- ✅ Navigation completes in under 2 seconds
- ✅ Tasks page displays user's tasks
- ✅ No errors in console

**Acceptance Criteria**:
- FR-005: Navigation to tasks page works ✓
- SC-006: Navigation completes in under 2 seconds ✓

---

### Scenario 4: Responsive Design - Mobile View (P2)

**User Story**: Professional Visual Design

**Steps**:
1. Navigate to `http://localhost:3000`
2. Open browser DevTools (F12)
3. Toggle device toolbar (Ctrl+Shift+M or Cmd+Shift+M)
4. Test the following device sizes:
   - Mobile: 375px × 667px (iPhone SE)
   - Tablet: 768px × 1024px (iPad)
   - Desktop: 1920px × 1080px

**Expected Outcomes**:
- ✅ Content remains readable at all screen sizes
- ✅ No horizontal scrolling
- ✅ Touch targets are at least 44px × 44px on mobile
- ✅ Text doesn't overflow containers
- ✅ Images/icons scale appropriately
- ✅ CTAs remain accessible
- ✅ Layout adapts gracefully (stacking on mobile)

**Acceptance Criteria**:
- FR-010: Responsive design works on all devices ✓
- SC-004: Functional layout from 320px to 2560px ✓

---

### Scenario 5: Visual Design Quality (P2)

**User Story**: Professional Visual Design

**Steps**:
1. Navigate to `http://localhost:3000`
2. Review visual design elements
3. Compare against design system specifications

**Expected Outcomes**:
- ✅ Typography follows hierarchy (3xl-5xl headlines, lg-xl subheadlines)
- ✅ Consistent spacing throughout (Tailwind spacing scale)
- ✅ Color palette is modern and accessible (WCAG AA contrast)
- ✅ Buttons have hover and focus states
- ✅ Cards have subtle shadows and rounded corners
- ✅ Smooth transitions and animations (60fps)
- ✅ Visual hierarchy emphasizes important actions
- ✅ Consistent design language with rest of application

**Acceptance Criteria**:
- FR-008: Modern styling with typography, colors, spacing ✓
- FR-009: Consistent design language ✓
- SC-003: 80% rate design as professional/modern ✓

---

### Scenario 6: Authentication State Timing (Edge Case)

**User Story**: Edge case handling

**Steps**:
1. Log in to the application
2. Keep the landing page (`http://localhost:3000`) open
3. Wait for JWT to expire (or manually clear cookies)
4. Refresh the page

**Expected Outcomes**:
- ✅ Page detects expired session
- ✅ UI transitions to unauthenticated state
- ✅ No error messages are displayed
- ✅ User sees Sign In/Create Account buttons
- ✅ No flash or jarring transitions

**Acceptance Criteria**:
- Edge case: Session expiry handled gracefully ✓

---

### Scenario 7: Performance Validation

**Steps**:
1. Navigate to `http://localhost:3000`
2. Open DevTools → Performance tab
3. Record page load
4. Analyze metrics

**Expected Outcomes**:
- ✅ LCP (Largest Contentful Paint) < 2.5 seconds
- ✅ FID (First Input Delay) < 100ms
- ✅ CLS (Cumulative Layout Shift) < 0.1
- ✅ Auth state check < 100ms
- ✅ Total page load < 1 second

**Acceptance Criteria**:
- Performance goals met ✓

---

## Manual Testing Checklist

Use this checklist to validate all acceptance criteria:

### Functional Requirements
- [ ] FR-001: Feature highlights displayed for unauthenticated users
- [ ] FR-002: User authentication status detected
- [ ] FR-003: Sign In/Create Account hidden for authenticated users
- [ ] FR-004: "Go to Tasks" button displayed for authenticated users
- [ ] FR-005: Navigation to tasks page works
- [ ] FR-006: User identification displayed
- [ ] FR-007: Logout option accessible
- [ ] FR-008: Modern professional styling applied
- [ ] FR-009: Consistent design language
- [ ] FR-010: Responsive design on all devices

### Success Criteria
- [ ] SC-001: Appropriate navigation within 1 second
- [ ] SC-002: Users can identify 3+ features within 10 seconds
- [ ] SC-003: Design rated as professional/modern
- [ ] SC-004: Functional layout from 320px to 2560px
- [ ] SC-005: Zero user confusion about auth state
- [ ] SC-006: Navigation to tasks < 2 seconds

### Edge Cases
- [ ] Session expiry handled gracefully
- [ ] Auth status errors handled without breaking UI
- [ ] Mobile screens (320px) display content correctly
- [ ] No flash of unauthenticated content (FOUC)

---

## Accessibility Testing

### Keyboard Navigation
- [ ] Tab through all interactive elements
- [ ] CTAs are reachable and clickable with Enter/Space
- [ ] Focus indicators are visible
- [ ] No keyboard traps

### Screen Reader Testing
- [ ] Heading hierarchy is logical (h1, h2, h3)
- [ ] Alt text for images/icons
- [ ] ARIA labels for dynamic content
- [ ] Loading states announced

### Color Contrast
- [ ] Text meets WCAG AA standards (4.5:1 for normal text)
- [ ] Button text is readable
- [ ] Focus indicators have sufficient contrast

---

## Troubleshooting

### Issue: Authentication state not detected
**Solution**:
1. Verify Better-Auth is configured correctly in `frontend/.env.local`
2. Check that `BETTER_AUTH_SECRET` matches backend `JWT_SECRET`
3. Verify backend is running and accessible

### Issue: Flash of unauthenticated content
**Solution**:
1. Ensure loading state is displayed during auth check
2. Verify Suspense boundary is in place
3. Check that `useAuth()` hook returns `isLoading` correctly

### Issue: Responsive design broken
**Solution**:
1. Check Tailwind breakpoints are correct
2. Verify CSS classes are applied conditionally
3. Test with actual devices, not just DevTools

### Issue: Page load is slow
**Solution**:
1. Optimize images (use Next.js Image component)
2. Reduce bundle size (check for unused dependencies)
3. Implement code splitting for non-critical components

---

## Next Steps

After validating all scenarios:

1. ✅ Mark all acceptance criteria as complete
2. 📝 Document any issues in GitHub issues
3. 🎯 Proceed to next priority user story or feature
4. 📊 Gather user feedback on design

---

## Contact & Support

For questions or issues:
- Check `CLAUDE.md` for project documentation
- Review constitution in `.specify/memory/constitution.md`
- Run `/sp.clarify` if requirements need refinement
