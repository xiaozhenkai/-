# -

解决github push错误The requested URL returned error: 403 Forbidden while accessing
2013年10月30日 ⁄ 综合 ⁄ 共 313字	⁄ 字号 小 中 大 ⁄ 评论关闭
github push错误：

git push
error: The requested URL returned error: 403 Forbidden while accessing https://github.com/wangz/future.git/info/refs
git version 1.7.1

OS:CENTOS

解决方案：

vim .git/config

修改

[remote "origin"]
	url = https://github.com/wangz/example.git
为：

[remote "origin"]
	url = https://wangz@github.com/wangz/example.git
- 再次git push，弹出框输入密码，即可提交

git:
   重命名文件或目录
     mv 命令
 
说明：重命名文件或目录（git mv 原文件名新文件名）
参数：无
操作：
