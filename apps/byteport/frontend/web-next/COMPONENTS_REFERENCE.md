# BytePort Component Reference - Quick Index

## Complete Component List

### shadcn/ui Base Components (27)
Location: `/Users/kooshapari/temp-PRODVERCEL/Rust/webApp/byte_port/frontend/web-next/components/ui/`

1. alert-dialog.tsx
2. alert.tsx
3. avatar.tsx
4. badge.tsx
5. button.tsx
6. card.tsx
7. checkbox.tsx
8. command.tsx
9. dialog.tsx
10. dropdown-menu.tsx
11. form.tsx
12. input.tsx
13. label.tsx
14. popover.tsx
15. progress.tsx
16. radio-group.tsx
17. scroll-area.tsx
18. select.tsx
19. separator.tsx
20. sheet.tsx
21. skeleton.tsx
22. switch.tsx
23. table.tsx
24. tabs.tsx
25. textarea.tsx
26. toast.tsx
27. tooltip.tsx

### Custom Components - Newly Created (4)
Location: `/Users/kooshapari/temp-PRODVERCEL/Rust/webApp/byte_port/frontend/web-next/components/`

1. **stat-card.tsx** - Dashboard statistics with progress and trends
2. **empty-state.tsx** - Empty state placeholders with actions
3. **loading-skeleton.tsx** - Loading state skeletons (9 variants)
4. **copy-button.tsx** - Copy-to-clipboard functionality

### Custom Components - Pre-existing (24+)
Location: `/Users/kooshapari/temp-PRODVERCEL/Rust/webApp/byte_port/frontend/web-next/components/`

Core Layout:
1. sidebar.tsx
2. header.tsx
3. theme-provider.tsx
4. theme-toggle.tsx

Cards:
5. deployment-card.tsx
6. service-card.tsx
7. metric-card.tsx
8. api-key-card.tsx
9. plan-card.tsx
10. setting-card.tsx

Display:
11. status-badge.tsx
12. status-indicator.tsx
13. provider-badge.tsx
14. log-viewer.tsx
15. realtime-log-viewer.tsx
16. terminal.tsx

Interactive:
17. command-palette.tsx
18. deployment-wizard.tsx
19. deployment-progress.tsx
20. deploy-button.tsx
21. provider-selector.tsx

Data & Charts:
22. metrics-chart.tsx
23. cost-chart.tsx
24. cost-breakdown.tsx
25. cost-tracker.tsx
26. usage-bar.tsx

Layout Helpers:
27. container.tsx
28. page-header.tsx
29. section.tsx

## Import Patterns

### shadcn/ui Components
```tsx
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
```

### Custom Components
```tsx
import { StatCard, StatGroup } from "@/components/stat-card"
import { EmptyState } from "@/components/empty-state"
import { LoadingSkeleton, LoadingSkeletonGrid } from "@/components/loading-skeleton"
import { CopyButton, CopyText } from "@/components/copy-button"
import { DeploymentCard } from "@/components/deployment-card"
import { Sidebar } from "@/components/sidebar"
```

## Component Categories

### Form Components
- button, input, textarea, label, checkbox, radio-group, switch, select, form

### Layout Components  
- card, separator, scroll-area, sheet, tabs, sidebar, container, section

### Feedback Components
- alert, alert-dialog, dialog, toast, progress, skeleton, badge, status-badge

### Navigation Components
- dropdown-menu, command, popover, tooltip, command-palette

### Data Display
- table, avatar, deployment-card, service-card, metric-card, stat-card

### Status & Indicators
- status-badge, status-indicator, provider-badge, progress

### Interactive
- copy-button, theme-toggle, deploy-button

### State Management
- empty-state, loading-skeleton

### Data Visualization
- metrics-chart, cost-chart, cost-breakdown, usage-bar

## File Paths

All components absolute paths:
```
/Users/kooshapari/temp-PRODVERCEL/Rust/webApp/byte_port/frontend/web-next/components/
├── ui/
│   ├── alert-dialog.tsx
│   ├── alert.tsx
│   ├── avatar.tsx
│   ├── badge.tsx
│   ├── button.tsx
│   ├── card.tsx
│   ├── checkbox.tsx
│   ├── command.tsx
│   ├── dialog.tsx
│   ├── dropdown-menu.tsx
│   ├── form.tsx
│   ├── input.tsx
│   ├── label.tsx
│   ├── popover.tsx
│   ├── progress.tsx
│   ├── radio-group.tsx
│   ├── scroll-area.tsx
│   ├── select.tsx
│   ├── separator.tsx
│   ├── sheet.tsx
│   ├── skeleton.tsx
│   ├── switch.tsx
│   ├── table.tsx
│   ├── tabs.tsx
│   ├── textarea.tsx
│   ├── toast.tsx
│   └── tooltip.tsx
├── api-key-card.tsx
├── command-palette.tsx
├── container.tsx
├── copy-button.tsx (NEW)
├── cost-breakdown.tsx
├── cost-chart.tsx
├── cost-tracker.tsx
├── deploy-button.tsx
├── deployment-card.tsx
├── deployment-progress.tsx
├── deployment-wizard.tsx
├── empty-state.tsx (NEW)
├── header.tsx
├── layout/
├── loading-skeleton.tsx (NEW)
├── log-viewer.tsx
├── metric-card.tsx
├── metrics-chart.tsx
├── page-header.tsx
├── plan-card.tsx
├── provider-badge.tsx
├── provider-selector.tsx
├── realtime-log-viewer.tsx
├── section.tsx
├── service-card.tsx
├── setting-card.tsx
├── sidebar.tsx
├── stat-card.tsx (NEW)
├── status-badge.tsx
├── status-indicator.tsx
├── terminal.tsx
├── theme-provider.tsx
├── theme-toggle.tsx
└── usage-bar.tsx
```

## Quick Stats

- **Total Components**: 59+
- **shadcn/ui**: 27
- **Custom**: 28+
- **Layout**: 4+
- **Newly Created**: 4
- **Pre-existing**: 24+
