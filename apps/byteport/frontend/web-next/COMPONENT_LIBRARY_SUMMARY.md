# BytePort UI Component Library

## Overview

Complete UI component library built with shadcn/ui, TypeScript, and Tailwind CSS for the BytePort application.

## Installation Complete

All shadcn/ui components have been successfully installed and configured.

## Component Categories

### 1. shadcn/ui Base Components (26 components)

Located in `/components/ui/`:

- **Form Controls:**
  - `button.tsx` - Versatile button with multiple variants
  - `input.tsx` - Text input field
  - `textarea.tsx` - Multi-line text input
  - `label.tsx` - Form labels
  - `checkbox.tsx` - Checkbox input
  - `radio-group.tsx` - Radio button groups
  - `switch.tsx` - Toggle switch
  - `select.tsx` - Dropdown select
  - `form.tsx` - Form field wrapper with validation

- **Layout:**
  - `card.tsx` - Card container with header, content, footer
  - `separator.tsx` - Visual divider
  - `scroll-area.tsx` - Custom scrollable area
  - `sheet.tsx` - Slide-out panel
  - `tabs.tsx` - Tabbed navigation

- **Feedback:**
  - `alert.tsx` - Alert messages
  - `alert-dialog.tsx` - Confirmation dialogs
  - `dialog.tsx` - Modal dialogs
  - `toast.tsx` - Toast notifications
  - `progress.tsx` - Progress bars
  - `skeleton.tsx` - Loading skeletons
  - `badge.tsx` - Status badges

- **Navigation:**
  - `dropdown-menu.tsx` - Dropdown menus
  - `command.tsx` - Command palette
  - `popover.tsx` - Popover tooltips
  - `tooltip.tsx` - Hover tooltips

- **Data Display:**
  - `table.tsx` - Data tables
  - `avatar.tsx` - User avatars

### 2. Custom Application Components (28 components)

Located in `/components/`:

#### Core Layout Components
- **`sidebar.tsx`** - Main navigation sidebar
  - Collapsible design
  - Active state highlighting
  - Dashboard, Deployments, Services, Monitoring, Projects, Costs, Settings
  - Tooltip support for collapsed state
  - Mobile responsive

- **`header.tsx`** - Application header
  - BytePort logo/branding
  - Command palette trigger (Cmd+K)
  - User menu with dropdown
  - Notifications bell with badge
  - Mobile menu toggle

- **`theme-provider.tsx`** - Theme context provider
  - next-themes integration
  - Dark/light/system modes
  - Persistent theme selection

- **`theme-toggle.tsx`** - Theme switcher button
  - Animated sun/moon icons
  - Smooth transitions

#### Card Components
- **`deployment-card.tsx`** - Deployment overview card
  - Status indicator with pulsing animation
  - Provider badge
  - Framework/runtime tags
  - URL with external link
  - Action menu (restart, stop, delete, view logs, settings)
  - Error message display
  - Created timestamp

- **`service-card.tsx`** - Service status card
  - Real-time status indicator
  - CPU/Memory/Disk usage with progress bars
  - Requests per minute metric
  - Uptime display
  - Service type badge
  - Action menu (start, stop, restart, settings, delete)

- **`metric-card.tsx`** - Metric display card
  - Large value display
  - Trend indicators (up/down/neutral)
  - Icon support
  - Status variants (success, warning, error, info)
  - Loading state
  - Prefix/suffix support
  - `MetricGroup` component for grid layouts

- **`stat-card.tsx`** - Dashboard statistics card
  - Compact and full variants
  - Progress bar integration
  - Change percentage display
  - Icon with custom styling
  - Variant colors (success, warning, error, info)
  - `StatGroup` component for responsive grids

- **`api-key-card.tsx`** - API key management card
- **`plan-card.tsx`** - Subscription plan card
- **`setting-card.tsx`** - Settings option card

#### Status & Display Components
- **`status-badge.tsx`** - Colored status badges
  - Animated icons for active states
  - Multiple status types:
    - Deployment: pending, building, deploying, running, failed, terminated
    - Service: online, offline, degraded
  - Customizable sizes (sm, md, lg)
  - Icon + label combinations

- **`status-indicator.tsx`** - Dot status indicator
  - Pulsing animation for active states
  - Size variants
  - Optional label display

- **`provider-badge.tsx`** - Cloud provider badges
  - Provider icons and names
  - Color-coded by provider

#### Interactive Components
- **`copy-button.tsx`** - Copy to clipboard button
  - Animated success feedback
  - Icon-only or with text
  - Multiple variants
  - `CopyCodeBlock` - Code block with copy button
  - `CopyText` - Inline or block text with copy

- **`command-palette.tsx`** - Global command palette
  - Keyboard shortcuts (Cmd+K)
  - Quick navigation
  - Search functionality

#### Data Display Components
- **`log-viewer.tsx`** - Log viewer component
  - Syntax highlighting
  - Auto-scroll
  - Search/filter
  - Copy functionality

- **`realtime-log-viewer.tsx`** - Real-time log streaming
- **`terminal.tsx`** - Terminal-style display
  - Monospace font
  - Dark theme
  - Command history

- **`metrics-chart.tsx`** - Metrics visualization
  - Time-series charts
  - Multiple data series
  - Responsive design

- **`cost-chart.tsx`** - Cost tracking charts
- **`cost-breakdown.tsx`** - Detailed cost breakdown
- **`cost-tracker.tsx`** - Cost monitoring widget
- **`usage-bar.tsx`** - Resource usage bar

#### State Components
- **`empty-state.tsx`** - Empty state placeholders
  - Customizable icon
  - Title and description
  - Primary and secondary actions
  - Three variants: default, minimal, card
  - `EmptyStateList` - Grid of getting started items

- **`loading-skeleton.tsx`** - Loading state skeletons
  - Multiple variants: card, list, table, deployment, metric, stat, form, text, avatar
  - Count support for multiple items
  - Compact mode
  - `LoadingSkeletonGrid` - Grid layout for skeletons

#### Workflow Components
- **`deployment-wizard.tsx`** - Multi-step deployment wizard
- **`deployment-progress.tsx`** - Deployment progress tracker
- **`deploy-button.tsx`** - Quick deploy button
- **`provider-selector.tsx`** - Cloud provider selection

#### Layout Helpers
- **`container.tsx`** - Page container wrapper
- **`page-header.tsx`** - Page header component
- **`section.tsx`** - Content section wrapper

### 3. Layout Components

Located in `/components/layout/`:
- App layout wrapper
- Authentication layout
- Dashboard layout
- Public layout
- Error boundaries

## Design System

### Color Palette
- Primary: Blue tones for actions and highlights
- Secondary: Gray tones for UI elements
- Success: Green for positive states
- Warning: Yellow for cautionary states
- Error/Destructive: Red for errors and destructive actions
- Muted: Subtle grays for less important content

### Typography
- Font Family: System font stack (default Next.js)
- Headings: Bold weights with proper hierarchy
- Body: Regular weight, optimized for readability
- Code: Monospace font for technical content

### Spacing
- Consistent spacing scale: 4px base unit
- Padding: p-2 to p-8 for components
- Gaps: gap-2 to gap-6 for layouts
- Margins: mt-2 to mt-8 for vertical spacing

### Border Radius
- Small: rounded-sm (2px)
- Default: rounded-md (6px)
- Large: rounded-lg (8px)
- Full: rounded-full (9999px)

## Component Patterns

### Card Pattern
Most data display components follow the Card pattern:
```tsx
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
    <CardDescription>Description</CardDescription>
  </CardHeader>
  <CardContent>
    {/* Main content */}
  </CardContent>
  <CardFooter>
    {/* Actions */}
  </CardFooter>
</Card>
```

### Status Display Pattern
Status components use consistent color coding:
- Green: Running/Online/Success
- Yellow: Pending/Warning/Degraded
- Blue: Building/Deploying/In Progress
- Red: Failed/Error/Offline
- Gray: Terminated/Inactive

### Action Menu Pattern
Interactive cards include dropdown action menus:
```tsx
<DropdownMenu>
  <DropdownMenuTrigger>
    <MoreVertical />
  </DropdownMenuTrigger>
  <DropdownMenuContent>
    <DropdownMenuItem>Action 1</DropdownMenuItem>
    <DropdownMenuItem>Action 2</DropdownMenuItem>
    <DropdownMenuSeparator />
    <DropdownMenuItem className="text-destructive">
      Delete
    </DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
```

## Responsive Design

All components are mobile-first and responsive:
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

Grid components support responsive columns:
- 1 column on mobile
- 2 columns on tablet
- 3-4 columns on desktop

## Accessibility

All components follow accessibility best practices:
- Semantic HTML
- ARIA labels and roles
- Keyboard navigation support
- Focus management
- Screen reader support
- Color contrast compliance

## Animation

Subtle animations enhance UX:
- Hover states with smooth transitions
- Loading skeletons with pulse animation
- Status indicators with pulsing for active states
- Theme toggle with rotating icons
- Toast notifications slide in/out
- Dialog/sheet animations

## Usage Examples

### Dashboard Stats
```tsx
import { StatGroup } from "@/components/stat-card"

const stats = [
  {
    title: "Total Deployments",
    value: "12",
    change: { value: 8, label: "from last month" },
    icon: Rocket,
    variant: "success"
  },
  // ... more stats
]

<StatGroup stats={stats} columns={4} />
```

### Deployment List
```tsx
import { DeploymentCard } from "@/components/deployment-card"

{deployments.map(deployment => (
  <DeploymentCard
    key={deployment.id}
    deployment={deployment}
    onView={handleView}
    onRestart={handleRestart}
    onDelete={handleDelete}
  />
))}
```

### Empty State
```tsx
import { EmptyState } from "@/components/empty-state"

<EmptyState
  icon={Rocket}
  title="No deployments yet"
  description="Get started by deploying your first application"
  action={{
    label: "New Deployment",
    onClick: () => router.push("/deployments/new")
  }}
  variant="card"
/>
```

### Loading State
```tsx
import { LoadingSkeletonGrid } from "@/components/loading-skeleton"

{loading ? (
  <LoadingSkeletonGrid variant="deployment" count={4} columns={2} />
) : (
  <DeploymentList deployments={deployments} />
)}
```

## Configuration

### Tailwind Config
Located at `/tailwind.config.ts`:
- Custom color palette
- Dark mode configuration
- Animation utilities
- Custom spacing scale

### Components Config
Located at `/components.json`:
- Component import aliases
- Style configuration
- Path settings

## Next Steps

1. **Theming**: Customize the color palette in `tailwind.config.ts`
2. **Icons**: Add more Lucide React icons as needed
3. **Forms**: Build complex forms using the form components
4. **Data Tables**: Implement sortable, filterable tables
5. **Charts**: Integrate Recharts for data visualization
6. **Notifications**: Set up toast notification system
7. **Command Palette**: Configure keyboard shortcuts

## Resources

- [shadcn/ui Documentation](https://ui.shadcn.com)
- [Radix UI Primitives](https://www.radix-ui.com)
- [Tailwind CSS](https://tailwindcss.com)
- [Lucide Icons](https://lucide.dev)

## File Structure

```
/components/
├── ui/                      # shadcn/ui base components (26 files)
├── layout/                  # Layout wrappers
├── deployment-card.tsx      # Deployment display
├── service-card.tsx         # Service status
├── metric-card.tsx          # Metrics with trends
├── stat-card.tsx            # Dashboard stats
├── status-badge.tsx         # Status indicators
├── empty-state.tsx          # Empty states
├── loading-skeleton.tsx     # Loading states
├── copy-button.tsx          # Copy functionality
├── sidebar.tsx             # Main navigation
├── header.tsx              # App header
├── theme-provider.tsx      # Theme context
├── theme-toggle.tsx        # Theme switcher
├── terminal.tsx            # Terminal display
├── log-viewer.tsx          # Log viewer
└── ... (15 more components)
```

## Total Component Count

- **shadcn/ui Components**: 26
- **Custom Components**: 28
- **Layout Components**: 4
- **Total**: 58+ components

All components are fully typed with TypeScript and follow consistent patterns for a polished, production-ready UI.
