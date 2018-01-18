# **UESTC-EAMS**

---

### **简介**

UESTC 教务系统的 Python 库，主要方便拓展应用。



还没填的坑：

* 查询课表
* 成绩查询
* 一些实际的应用（如抢课等）
* ...



*依赖的三方库：* **requests**

---

### **快速上手**

```python
import uestc_eams
```

1.  **认证登录**

   使用 **Login()** 方法认证并创建一个 Session。若登录成功，**Login()** 方法返回一个 **EAMSSession** 对象。

   ```python
   session = uestc_emas.Login(_username = '2016xxxxxxxxx', _password = 'xxxxxx')
   ```

   或者使用 **EAMSSession.Login()** 进行认证。

   ```python
   session = uestc_eams.EAMSSession()
   EAMSSession.Login(_username = '2016xxxxxxxxx', _password = 'xxxxxx')
   ```

   在操作过程中，**EAMSSession** 将自动管理登录状态（例如会话过期后的处理），不需要对 **EAMSSession** 进行额外操作。

   若需要登出，可以使用 **EAMSSession.Logout()**。


