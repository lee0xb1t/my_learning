package res

import "github.com/gin-gonic/gin"

type Response struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
	Data    any    `json:"data"`
}

var codeMap = map[int]string{
	1001: "权限错误",
	1002: "角色错误",
}

func response(c *gin.Context, code int, data any, msg string) {
	c.JSON(200, Response{
		Code: code, Data: data, Message: msg,
	})
}

func Ok(c *gin.Context, data any, msg string) {
	response(c, 0, data, msg)
}

func OkWithMsg(c *gin.Context, msg string) {
	response(c, 0, gin.H{}, msg)
}

func OkWithData(c *gin.Context, data any) {
	response(c, 0, data, "success")
}

func Fail(c *gin.Context, data any, msg string) {
	response(c, 0, data, msg)
}

func FailWithMsg(c *gin.Context, msg string) {
	response(c, 0, gin.H{}, msg)
}

func FailWithCode(c *gin.Context, code int) {
	msg, ok := codeMap[code]
	if !ok {
		msg = "服务错误"
	}
	response(c, code, nil, msg)
}
