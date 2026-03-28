package main

import (
	"net/http"
	"nvms/deploy"

	spinhttp "github.com/fermyon/spin-go-sdk/http"
	"github.com/julienschmidt/httprouter"
)

/*************  ✨ Codeium Command ⭐  *************/
// The init function is called automatically by Spin when the application is loaded.
// It handles all incoming HTTP requests by routing them to the appropriate handler
// function.
/******  80e072a9-63cd-4dd7-bfcb-c767f804f8a9  *******/

func init() {
	spinhttp.Handle(func(w http.ResponseWriter, r *http.Request) {
		router := initRouter()
		router.ServeHTTP(w, r)
	})
   
}
func initRouter() *spinhttp.Router{
	router := spinhttp.NewRouter()
	router.POST("/",  validateAction(deploy.DeployProject))
	router.POST("/deploy",  validateAction(deploy.DeployProject))
	return router;
}
func validateAction(handler http.HandlerFunc) httprouter.Handle {
    return func(w http.ResponseWriter, r *http.Request, _ httprouter.Params) {
        /*err := lib.AuthMiddleware(w, r)
		if err != nil {
			http.Error(w, "Unauthorized", http.StatusUnauthorized)
			return
		} else {*/
        handler(w, r)
		/*}
		return*/
    }
}
func main() {}