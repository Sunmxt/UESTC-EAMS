# **UESTC-EAMS**

---

### **简介**

UESTC 教务系统的 Python 库，主要方便拓展应用。


还没填的坑：

* 查询课表
* 成绩查询
* 一些实际的应用（如抢课等）
* ...

除基本库外，还提供少量的应用，包含在 app 内。(也属于要填的坑)

目前还是有动力去填坑的，别担心。

*依赖的三方库：* **requests**

---

### **快速上手**

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

     目前有两种选课类型：**权重**、**抢课**，它们的值各对应 **uestc_eams.CASH**和**uestc_eams.CATCH**。

   - **查看可选课程：**

     ```python
     session.ElectCourse.Platform['A'].Courses
     ```

     **Courses** 是 **list** 对象。格式如下：

     ```python
     [
        {
       	   'name' : 课程名称
       	   , 'id' : 课程ID
       	   , 'credits' : 学分
       	   , 'teachers' : 任课老师。(tuple 对象)
       	   , 'campus' : 校区
       	   , 'remark' : 备注
            , 'start_week' : 起始周
            , 'end_week' : 结束周
            , 'exam' : 考试时间
            , 'week_hour' : 周学时
            , 'type' : 课程性质
            , 'room' : 上课教室
       }
       , ...
     ]
     ```

   - **查询课程容量**

     以查询 ID 为 305362 的课程为例。

     ```python
     session.ElectCourse.Platform['A'].Counts[305362]
     ```

     ```python
     {
         'cross_limit': 跨院系选课人数上限,
         'current': 当前平台已选人数,
         'current_a': A平台已选人数,
         'current_b': B平台已选人数,
         'current_c': C平台已选人数,
         'limit': 人数上限
     }
     ```

     ​

   - **选课/退课：**

     平台接口类提供了 **Elect()** 方法。目前仅支持抢课制。权重制和权重修改将在后续加入。

     - 例：选择A平台，ID为305362的课程。

       ```python
       session.ElectCourse.Platform['A'].Elect(305362, uestc_eams.ELECT)
       ```

     - 例：退掉 ID 为 305362 的课程

       ```python
       session.ElectCourse.Platform['A'].Elect(305362, uestc_eams.CANCEL)
       ```

