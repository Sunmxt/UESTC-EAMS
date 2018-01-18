# **UESTC-EAMS**

---

### **简介**

UESTC 教务系统的 Python 库，主要方便拓展应用。



*Note : 目前由于选课未开放，所有选课相关的接口都没有进行实际的测试，只完成了大部分逻辑，会在后面继续完善。*



还没填的坑：

* 查询课表
* 成绩查询
* 一些实际的应用（如抢课等）
* ...

除基本库外，还提供少量的应用，包含在 app 内。



*依赖的三方库：* **requests**

---

### 快速上手

```python
import uestc_eams
```

1. **认证登录**

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

2. **选课**

   **EAMSSession** 类实现了 **ElectCourse** 接口，包含选课平台的各种操作。

   ```python
   session.ElectCourse.Platform
   ```

   **session.ElectCourse.Platform** 是一个 **dict** 对象，其提供了**平台名称**和**操作接口**的映射：

   ```python
   { 平台名称1 : 接口1, 平台名称2 : 接口2, ...}
   ```

   例如，获取A平台的接口类：

   ```python
   session.ElectCourse.Platform['A']
   ```

   ​

   - **查看选课是否开启:**

     ```python
     session.ElectCourse.Opened
     ```

   - **查看平台的选课类型(以A平台为例)：**

     ```python
     session.ElectCourse.Platform['A'].ElectType
     ```

     目前有两种选课类型：**权重**、**抢课**，它们的值各对应 **EAMSSession.CASH**和**EAMSSession.CATCH**。

   - **查看可选课程信息：**

     ```python
     session.ElectCourse.Platform['A'].Courses
     ```

     **Courses** 是 **dict** 对象。格式如下：

     ```python
     {
       课程ID : {
       	'number' : 课程序号
       	, 'credits' : 学分
       	, 'campus' : 校区
       	, 'remark' : 备注
       	, 'exam' : 考试时间
       	, 'arrange' : 上课时间
       }
       , ...
     }
     ```

   - **选课/退课：**

     平台接口类提供了 **Elect()** 方法。

     - 例：选择A平台，ID为305362的课程。

       若为**权重制**，权重20分：

       ```python
       session.ElectCourse.Platform['A'].Elect(305362, EAMSSession.ELECT, 20)
       ```

       若为**抢课制**：

       ```python
       session.ElectCourse.Platform['A'].Elect(305362, EAMSSession.ELECT)
       ```

     - 例：退掉 ID 为 305362 的课程

       ```python
       session.ElectCourse.Platform['A'].Elect(305362, EAMSSession.CANCEL)
       ```

       ​


