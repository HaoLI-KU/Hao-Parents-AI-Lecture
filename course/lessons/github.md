# 共同练习｜爸妈第一次用 GitHub

状态：共同练习 · 备用

## 1. 各自注册并登录

两人在自己的 Mac 上打开 [GitHub 注册页](https://github.com/signup)，各自注册个人账号，按网页提示完成邮箱验证。登录后点右上角头像，确认用户名是自己的。登录、验证码和授权由本人完成，遇到卡点先停下来一起看。 [GitHub 账号注册说明](https://docs.github.com/en/account-and-profile/how-tos/account-management/creating-an-account-on-github)

## 2. 新建仓库时，先看可见性

各自打开 [新建 GitHub 仓库](https://github.com/new)，确认 Owner 是自己的账号。爸爸可取名 `technical-manual`，妈妈可取名 `my-first-repo`。课堂先选 **Private**，创建后检查仓库名称旁是否显示 Private。

| 选项 | 谁能看到 |
|---|---|
| Private（私有） | 自己和获授权的人。爸爸的手册和妈妈的小项目先用这个选项。 |
| Public（公开） | 任何人都可以查看仓库里的文件和公开提交历史。以后要公开自己的小项目时，再一起核对素材和发布范围。 |

私有仓库里也只放有权上传的文件。手册先选已确认可上传的 `.tex`、Markdown 规则和示例图表。账号信息、密钥、无权上传的内部资料留在本机。妈妈先用自己的一组虚构练习文件。 [GitHub 仓库可见性说明](https://docs.github.com/en/repositories/creating-and-managing-repositories/about-repositories)

## 3. 认三个词，让 Harness 帮忙执行

本节默认已经装好 DeepSeek Harness（爸爸第 2 节、妈妈第 6 节）。

- **clone（克隆）**：把 GitHub 仓库复制到电脑，得到可以编辑的本地项目。
- **commit（提交）**：在本地保存一份带说明的版本记录。
- **push（推送）**：把已提交的版本送到指定的 GitHub 仓库。

1. 在新仓库复制地址。各自在 Mac 选一个空练习位置，让 Harness 把仓库克隆到那里。若 GitHub 要求本机登录或授权，按提示由本人完成，再让 Harness 继续。
2. 打开克隆得到的文件夹。爸爸复制选好的手册文件，妈妈复制自己的 `index.html` 或那节课用到的练习文件。原来的本地项目仍可直接打开。复制前先看仓库里有没有 `.gitignore`；没有就建一个，至少排除 `.DS_Store`、密钥文件和私人草稿。
3. 用自然语言交代任务。先让 Harness 列出要上传的内容，自己检查后再同意推送。若 Harness 不能直接执行 git，就让它给出命令，由本人打开「终端」逐条执行并核对输出。

> 这个本地文件夹来自我刚建立的私有 GitHub 仓库。请核对远端地址和仓库所有者，列出准备提交的文件、分支和提交说明。只提交我刚复制进去、确认可上传的项目文件。不要提交密钥、账号资料或私人原件。等我确认后再提交和推送。需要登录或权限时先停下来告诉我。

4. 回到浏览器刷新各自的仓库，检查仍显示 Private，文件和提交说明都出现了。爸爸打开一份手册源文件，妈妈打开 `index.html`。看得见文件，就完成了第一次推送。

[克隆仓库](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) · [提交和推送入门](https://docs.github.com/en/repositories/creating-and-managing-repositories/quickstart-for-repositories)

本节只练文件推送。以后要让家人从网址打开自己的页面时，再单独配置 GitHub Pages 和确认发布范围。 [GitHub Pages 说明](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)
