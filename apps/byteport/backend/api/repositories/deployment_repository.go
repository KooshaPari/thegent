package repositories

import (
	"database/sql/driver"
	"encoding/json"
	"fmt"
	"sync"
	"time"

	"github.com/google/uuid"
	"gorm.io/gorm"
)

// EnvVarMap is a custom type that implements the GORM Scanner and Valuer interfaces
type EnvVarMap map[string]string

// Value implements driver.Valuer interface for GORM
func (e EnvVarMap) Value() (driver.Value, error) {
	if e == nil {
		return nil, nil
	}
	return json.Marshal(e)
}

// Scan implements sql.Scanner interface for GORM
func (e *EnvVarMap) Scan(value interface{}) error {
	if value == nil {
		*e = make(EnvVarMap)
		return nil
	}
	
	bytes, ok := value.([]byte)
	if !ok {
		return fmt.Errorf("failed to unmarshal EnvVarMap value: %v", value)
	}
	
	return json.Unmarshal(bytes, e)
}

// Deployment represents a deployment in the system
type Deployment struct {
	ID        string            `json:"id" gorm:"type:uuid;primary_key"`
	Name      string            `json:"name" gorm:"not null"`
	Type      string            `json:"type" gorm:"not null"` // frontend, backend, database
	Provider  string            `json:"provider" gorm:"not null"`
	Status    string            `json:"status" gorm:"not null;default:'pending'"`
	URL       string            `json:"url"`
	GitURL    string            `json:"git_url"`
	Branch    string            `json:"branch"`
	EnvVars   EnvVarMap         `json:"env_vars" gorm:"type:jsonb"`
	UserID    string            `json:"user_id" gorm:"type:uuid;index"`
	CreatedAt time.Time         `json:"created_at"`
	UpdatedAt time.Time         `json:"updated_at"`
}

// DeploymentRepository defines the interface for deployment data operations
type DeploymentRepository interface {
	Create(deployment *Deployment) error
	GetByID(id string) (*Deployment, error)
	GetByUserID(userID string) ([]*Deployment, error)
	Update(deployment *Deployment) error
	Delete(id string) error
	List() ([]*Deployment, error)
	GetByStatus(status string) ([]*Deployment, error)
	GetByProvider(provider string) ([]*Deployment, error)
}

// GormDeploymentRepository implements DeploymentRepository using GORM
type GormDeploymentRepository struct {
	db *gorm.DB
}

// NewGormDeploymentRepository creates a new GORM-based deployment repository
func NewGormDeploymentRepository(db *gorm.DB) *GormDeploymentRepository {
	return &GormDeploymentRepository{db: db}
}

func (r *GormDeploymentRepository) Create(deployment *Deployment) error {
	if deployment.ID == "" {
		deployment.ID = uuid.New().String()
	}
	deployment.CreatedAt = time.Now()
	deployment.UpdatedAt = time.Now()
	
	return r.db.Create(deployment).Error
}

func (r *GormDeploymentRepository) GetByID(id string) (*Deployment, error) {
	var deployment Deployment
	err := r.db.Where("id = ?", id).First(&deployment).Error
	if err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, nil
		}
		return nil, err
	}
	return &deployment, nil
}

func (r *GormDeploymentRepository) GetByUserID(userID string) ([]*Deployment, error) {
	var deployments []*Deployment
	err := r.db.Where("user_id = ?", userID).Find(&deployments).Error
	return deployments, err
}

func (r *GormDeploymentRepository) Update(deployment *Deployment) error {
	deployment.UpdatedAt = time.Now()
	return r.db.Save(deployment).Error
}

func (r *GormDeploymentRepository) Delete(id string) error {
	return r.db.Where("id = ?", id).Delete(&Deployment{}).Error
}

func (r *GormDeploymentRepository) List() ([]*Deployment, error) {
	var deployments []*Deployment
	err := r.db.Find(&deployments).Error
	return deployments, err
}

func (r *GormDeploymentRepository) GetByStatus(status string) ([]*Deployment, error) {
	var deployments []*Deployment
	err := r.db.Where("status = ?", status).Find(&deployments).Error
	return deployments, err
}

func (r *GormDeploymentRepository) GetByProvider(provider string) ([]*Deployment, error) {
	var deployments []*Deployment
	err := r.db.Where("provider = ?", provider).Find(&deployments).Error
	return deployments, err
}

// InMemoryDeploymentRepository implements DeploymentRepository using in-memory storage
// This is useful for testing without a database
type InMemoryDeploymentRepository struct {
	deployments map[string]*Deployment
	mu          sync.RWMutex
}

// NewInMemoryDeploymentRepository creates a new in-memory deployment repository
func NewInMemoryDeploymentRepository() *InMemoryDeploymentRepository {
	return &InMemoryDeploymentRepository{
		deployments: make(map[string]*Deployment),
	}
}

func (r *InMemoryDeploymentRepository) Create(deployment *Deployment) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	
	if deployment.ID == "" {
		deployment.ID = uuid.New().String()
	}
	deployment.CreatedAt = time.Now()
	deployment.UpdatedAt = time.Now()
	
	r.deployments[deployment.ID] = deployment
	return nil
}

func (r *InMemoryDeploymentRepository) GetByID(id string) (*Deployment, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	
	deployment, exists := r.deployments[id]
	if !exists {
		return nil, nil
	}
	
	// Return a copy to avoid race conditions
	copy := *deployment
	return &copy, nil
}

func (r *InMemoryDeploymentRepository) GetByUserID(userID string) ([]*Deployment, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	
	var deployments []*Deployment
	for _, deployment := range r.deployments {
		if deployment.UserID == userID {
			copy := *deployment
			deployments = append(deployments, &copy)
		}
	}
	
	return deployments, nil
}

func (r *InMemoryDeploymentRepository) Update(deployment *Deployment) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	
	if _, exists := r.deployments[deployment.ID]; !exists {
		return fmt.Errorf("deployment with id %s not found", deployment.ID)
	}
	
	deployment.UpdatedAt = time.Now()
	r.deployments[deployment.ID] = deployment
	return nil
}

func (r *InMemoryDeploymentRepository) Delete(id string) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	
	if _, exists := r.deployments[id]; !exists {
		return fmt.Errorf("deployment with id %s not found", id)
	}
	
	delete(r.deployments, id)
	return nil
}

func (r *InMemoryDeploymentRepository) List() ([]*Deployment, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	
	deployments := make([]*Deployment, 0, len(r.deployments))
	for _, deployment := range r.deployments {
		copy := *deployment
		deployments = append(deployments, &copy)
	}
	
	return deployments, nil
}

func (r *InMemoryDeploymentRepository) GetByStatus(status string) ([]*Deployment, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	
	var deployments []*Deployment
	for _, deployment := range r.deployments {
		if deployment.Status == status {
			copy := *deployment
			deployments = append(deployments, &copy)
		}
	}
	
	return deployments, nil
}

func (r *InMemoryDeploymentRepository) GetByProvider(provider string) ([]*Deployment, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	
	var deployments []*Deployment
	for _, deployment := range r.deployments {
		if deployment.Provider == provider {
			copy := *deployment
			deployments = append(deployments, &copy)
		}
	}
	
	return deployments, nil
}