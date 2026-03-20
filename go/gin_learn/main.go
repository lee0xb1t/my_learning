package main

import (
	"fmt"
	"gin_learn/res"
	"io"

	"github.com/gin-gonic/gin"
)

func main() {
	r := gin.Default()

	r.Static("st", "static")
	r.StaticFile("abc", "static/abc.txt")

	r.LoadHTMLGlob("templates/*")

	r.GET("/", func(c *gin.Context) {
		c.HTML(200, "index.html", map[string]any{
			"title": "666",
		})
	})

	r.GET("/file", func(c *gin.Context) {
		c.FileAttachment("main.go", "main.go")
		c.File("main.go")
	})

	r.GET("/ping", func(c *gin.Context) {
		res.OkWithData(c, gin.H{})
	})

	/* http://127.0.0.1:8080/query/1?name=111&gender=1&gender=2&gender=3 */
	r.GET("/query/:id", func(c *gin.Context) {
		fmt.Println(c.Params.Get("aa"))

		res.OkWithData(c, gin.H{
			"id":     c.Param("id"),
			"name":   c.Query("name"),
			"age":    c.DefaultQuery("age", "22"),
			"gender": c.QueryArray("gender"),
		})
	})

	r.POST("/users", func(c *gin.Context) {
		fileHeader, err := c.FormFile("file")
		if err != nil {
			res.FailWithMsg(c, "文件为空")
		}

		fmt.Println(fileHeader.Header)
		fmt.Println(fileHeader.Size)
		fmt.Println(fileHeader.Filename)

		file, _ := fileHeader.Open()
		bytes, _ := io.ReadAll(file)
		fmt.Println(bytes)

		id := c.PostForm("id")
		res.OkWithData(c, gin.H{
			"id": id,
		})
	})

	r.POST("/books", func(c *gin.Context) {
		id := c.PostForm("id")
		res.OkWithData(c, gin.H{
			"id": id,
		})
	})

	err := r.Run(":8080")
	if err != nil {
		panic(err)
	}
}
