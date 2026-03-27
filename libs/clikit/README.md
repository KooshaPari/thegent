# clikit

Go CLI toolkit with dependency injection and modular command structure. Build professional command-line tools with minimal boilerplate.

## Features

- Dependency injection container
- Modular command structure
- Configuration management
- Plugin system
- Error handling
- Progress bars
- Interactive prompts
- Table output

## Installation

```bash
go get github.com/KooshaPari/clikit
```

## Usage

### Basic CLI

```go
package main

import (
    "context"
    "os"

    "github.com/KooshaPari/clikit/cli"
    "github.com/KooshaPari/clikit/commands"
)

func main() {
    app := cli.New("myapp", "A wonderful CLI tool").
        WithVersion("1.0.0").
        WithCommands(
            commands.NewHelloCommand(),
            commands.NewServeCommand(),
        )

    ctx := context.Background()
    if err := app.Run(ctx, os.Args[1:]); err != nil {
        os.Exit(1)
    }
}
```

### Commands

```go
type HelloCommand struct{}

func (c *HelloCommand) Name() string     { return "hello" }
func (c *HelloCommand) Usage() string     { return "hello [name]" }
func (c *HelloCommand) Short() string     { return "Say hello" }

func (c *HelloCommand) Run(ctx context.Context, args []string) error {
    name := "World"
    if len(args) > 0 {
        name = args[0]
    }
    fmt.Printf("Hello, %s!\n", name)
    return nil
}
```

### DI Container

```go
container := di.New()
container.Singleton(&Database{}, func() (*Database, error) {
    return NewDatabase(os.Getenv("DATABASE_URL"))
})
container.Singleton(&Logger{}, func() (*Logger, error) {
    return NewLogger(os.Getenv("LOG_LEVEL"))
})

var db *Database
container.Get(&db)
```

## Architecture

```
src/
├── cli/              # Core CLI framework
│   ├── App.go
│   ├── Command.go
│   └── Flag.go
├── di/              # Dependency injection
│   └── Container.go
├── config/          # Configuration
├── plugin/          # Plugin system
└── output/         # Formatted output
    ├── table.go
    ├── progress.go
    └── prompt.go
```

## License

MIT
