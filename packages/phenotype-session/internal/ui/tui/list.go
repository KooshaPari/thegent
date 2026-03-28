package tui

import (
	"fmt"
	"strings"
	"time"

	tea "github.com/charmbracelet/bubbletea"

	"github.com/KooshaPari/phenotype-session/internal/model"
	"github.com/KooshaPari/phenotype-session/internal/store"
)

type ListModel struct {
	store         store.Store
	Sessions      []model.SessionMeta
	SelectedIndex int
	Filter        string
	SortBy        string
	Width, Height int
	Quit          bool
	Err           error
}

func NewListModel(st store.Store) ListModel {
	m := ListModel{
		store:         st,
		Sessions:      []model.SessionMeta{},
		SelectedIndex: 0,
		Filter:        "",
		SortBy:        "updated_by",
	}
	// load synchronously for simplicity
	ses, err := st.ListSessions(store.SessionFilter{All: true, SortBy: m.SortBy, Limit: 200})
	if err == nil {
		m.Sessions = ses
	} else {
		m.Err = err
	}
	return m
}

func (m ListModel) Init() tea.Cmd {
	return nil
}

func (m ListModel) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "q", "ctrl+c":
			m.Quit = true
			return m, tea.Quit
		case "j", "down":
			if m.SelectedIndex < len(m.Sessions)-1 {
				m.SelectedIndex++
			}
			return m, nil
		case "k", "up":
			if m.SelectedIndex > 0 {
				m.SelectedIndex--
			}
			return m, nil
		case "enter":
			if len(m.Sessions) == 0 {
				return m, nil
			}
			s := m.Sessions[m.SelectedIndex]
			// For prototype: "open" prints to stdout via Quit with message
			fmt.Printf("open session: %s (harness=%s provider=%s model=%s)\n", s.ID, s.Harness, s.Provider, s.Model)
			return m, tea.Quit
		case "/":
			// toggle filter prompt: for prototype, clear filter
			if m.Filter == "" {
				m.Filter = "type-filter:" // placeholder
			} else {
				m.Filter = ""
			}
			return m, nil
		case "s":
			// cycle sort
			switch m.SortBy {
			case "updated_by":
				m.SortBy = "updated_at"
			case "updated_at":
				m.SortBy = "name"
			default:
				m.SortBy = "updated_by"
			}
			// reload
			ses, err := m.store.ListSessions(store.SessionFilter{All: true, SortBy: m.SortBy, Limit: 200})
			if err == nil {
				m.Sessions = ses
				if m.SelectedIndex >= len(m.Sessions) {
					m.SelectedIndex = len(m.Sessions) - 1
					if m.SelectedIndex < 0 {
						m.SelectedIndex = 0
					}
				}
			} else {
				m.Err = err
			}
			return m, nil
		}
	}
	return m, nil
}

func (m ListModel) View() string {
	var b strings.Builder
	b.WriteString("pheno-session TUI (prototype) — q to quit, Enter open, s cycle sort\n\n")
	if m.Err != nil {
		fmt.Fprintf(&b, "error loading sessions: %v\n\n", m.Err)
	}
	if len(m.Sessions) == 0 {
		b.WriteString("(no sessions)\n")
		return b.String()
	}
	// Table header
	fmt.Fprintf(&b, "%-3s %-20s %-8s %-12s %-16s %-16s\n", "", "NAME", "HARNESS", "MODEL", "UPDATED_BY", "UPDATED_AT")
	for i, s := range m.Sessions {
		prefix := "  "
		if i == m.SelectedIndex {
			prefix = "→ "
		}
		updated := shortTime(s.UpdatedAt)
		name := s.Name
		if len(name) > 20 {
			name = name[:17] + "..."
		}
		fmt.Fprintf(&b, "%s %-20s %-8s %-12s %-16s %-16s\n", prefix, name, s.Harness, s.Model, s.UpdatedBy, updated)
	}
	return b.String()
}

// Run launches the Bubble Tea program and blocks until it exits.
func Run(m ListModel) error {
	p := tea.NewProgram(m)
	_, err := p.Run()
	return err
}

// shortTime helps display time compactly.
func shortTime(t time.Time) string {
	if t.IsZero() {
		return "-"
	}
	return t.Format("2006-01-02 15:04")
}
