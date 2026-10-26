# 推广素材：隐私自查

> 发出去之前，扫一遍手机号、身份证、地址、快递单号。

下面每条文案都用本仓脚本测过 AI 味。

---

## 一、GitHub 仓库元信息

**About**：见仓库设置（已由发布脚本写入）。

**Social preview**：`market/social-preview.png`（1280×640，已生成）。


---

## 二、小红书

**标题（5 选 1）**

1. 发截图前，请一定检查这 10 个地方
2. 我把自己的帖子扫了一遍，发现 6 处泄露
3. 打码没用：你的截图里还藏着这些信息
4. 发小红书前我都会跑一遍这个脚本
5. 别再用马赛克了，教你怎么正确打码

**正文**

有个朋友发帖被扒出了小区名字，原因是她只裁掉了门牌号，忘了聊天截图顶上的备注名。

我顺手做了个检查工具，先说自己踩的坑。

我写了一段「分享收快递体验」的草稿，跑了一遍，**命中 6 处**：

❗ 手机号（必删）
❗ 身份证号（必删，这条我还写了「要寄过去才能改地址」，等于把操作流程也告诉别人了）
⚠️ 详细地址 + 房号（建议删）
⚠️ 快递单号（建议删，能反查手机尾号和大致的投递地址）
· 微信号（平台也违规）

单项看着都不致命。但组合起来是：

**手机号 + 门牌号 + 「我这两天在家等快递」= 这个人现在家里有快递，且我能联系上他。**

改完之后是这样：

「快递等了两天，客服电话打了四遍。我们小区快递柜满了，只能放驿站。驿站离我家 1.2 公里，来回一趟 40 分钟。」

改动思路：**用具体数字替代具体位置**。1.2 公里、40 分钟，信息量更大，风险归零。

还有一条最重要的：**打码不等于遮住**。

半透明马赛克、只遮中间四位、局部涂抹，都可能被还原或推断。要么整块涂黑，要么裁掉。

脚本读不了图片，所以我整理了「截图必查 10 项」，第一条就是聊天截图顶部的备注名——那里通常写着真名 + 公司 + 职位。

零依赖，MIT。

`#隐私` `#安全` `#自媒体` `#小红书运营` / `#个人信息保护` `#打码` `#截图` `#避坑` / `#我的经验分享`

**首评（置顶）**

补一个细节：脚本输出里我自己也把号码打码了（13*******78）。因为如果你截图转发了这份报告，完整号码就又多了一份副本。


---

## 三、X / Twitter（英文）

```
A friend got doxxed from a post. What leaked wasn't her ID number — it was the contact name at the top of a chat screenshot (real name + company + title).

Built a pre-publish scanner. Mine flagged 6 items in a "just sharing my delivery experience" draft:

→ phone number, ID number
→ street address + unit number
→ tracking number (reverse-lookups phone + area)
→ WeChat ID

None of them alone is fatal. Together: phone + unit number + "I've been home
waiting two days" = this person is home, has a package, and is reachable.

Fix: replace location with *magnitude*. "1.2 km away, 40 minutes round trip"
carries more information and zero risk.

Also: mosaic isn't redaction. Small areas can be partially reconstructed.
Black it out or crop it.
```


---

## 四、Show HN

```
Show HN: Privacy-scan – check a post for leaked personal data before you publish it

A friend was identified from a public post. The leak wasn't her ID number — it
was the contact name in a chat screenshot (real name, employer, job title), plus
a unit number, plus "I've been home waiting for this package for two days."

Individually harmless. Combined: someone is home, has a parcel, and is reachable.

The scanner runs 12 rule classes over text (ID, phone, bank card, license plate,
email, tracking numbers, street addresses, unit numbers, WeChat/QQ, internal
hostnames, employee IDs, full birthdates) in three severity tiers.

Two design decisions:

1. **The report masks values too** (`13*******78`). If you screenshot the report
   and share it, you'd otherwise create another copy of the secret.
2. **It gives a fix per hit**, not just a flag: "delete it" vs "blank it out
   entirely" vs "keep the district, drop the street."

Honest limitation: it cannot read images. Text only. So it ships with a 10-item
manual checklist for screenshots — top-of-chat contact name, group name, input
field drafts, status bar, notification banners, order numbers, background
whiteboards, reflections, EXIF.

github.com/zhbehx/privacy-scan
```


---

## 五、发布清单

| 渠道 | 素材 | 关键动作 |
| --- | --- | --- |
| GitHub | Release v1.0.0 | 已发布 |
| X | 上面的英文稿 | 配终端截图，分数可见 |
| Show HN | 上面的 HN 稿 | 周二至周四 UTC 14:00–16:00 |
| 社群 / 即刻 | 一句话 + 链接 | 只讲一个点，别贴 README |