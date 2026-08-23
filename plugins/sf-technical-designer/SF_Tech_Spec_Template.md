<!--
  מקור האמת למבנה מסמך האפיון הטכני. נקרא דינמית בזמן ריצה (Guardrail #3).
  עריכת קובץ זה משנה את מבנה ה-DOCX שנוצר — ללא שינוי קוד.

  קונבנציות ל-parser (Phase 4):
    # כותרת            -> כותרת המסמך (Title / H0)
    ## N. כותרת        -> פרק ראשי קבוע (Heading level 1) — מחייב, כותרת מדויקת
    ### N.M כותרת      -> תת-פרק (Heading level 2)
    #### כותרת         -> תת-תת-פרק (Heading level 3)
    **תווית:**         -> שדה שה-Document Generator ממלא (תיאור/לוגיקה בעברית)
    - פריט             -> פריט ברשימת תבליטים
    טבלת markdown       -> טבלה. שורת הכותרת = שמות העמודות (סכמה).
    [FIELD-TABLE]       -> הטבלה הבאה היא טבלת מפתח/ערך (פרטי פרויקט)
    [REPEAT: <תיאור>]   -> הבלוק הבא הוא תבנית חוזרת: מופע אחד לכל פריט (אוטומציה/טופס/מסך).
                           הכותרות שלו דינמיות לפי הפריט — לא חלק מרשימת הכותרות הקבועה.
    ```text ... ```     -> בלוק דיאגרמה/קוד: monospace, LTR, שמירת רווחים (Data Flow / ERD)
    [PAGEBREAK]         -> מעבר עמוד

  כללי שפה ו-RTL (נאכפים בקוד הרינדור + בפרומפט):
    - מונחי Salesforce (Object/API/Flow names, Apex, LWC) באנגלית.
    - תיאורים ולוגיקה עסקית בעברית.
    - כל המסמך RTL אמיתי (bidi); טבלאות RTL (bidiVisual) — הסדר הויזואלי מתהפך אוטומטית.
    - מזהי קוד/API נשארים LTR בתוך משפט עברי.
    - בלוקי דיאגרמה/קוד נשארים LTR + monospace במלואם.
    - פרק ללא תוכן: לכתוב "לא רלוונטי" — לא להשמיט.
-->

# מסמך אפיון טכני - [שם המשימה]

מטרת המסמך: תיעוד טכני של המשימה לטובת פיתוח, תחזוקה עתידית, תחקור, בדיקות QA והבנת השפעה (Impact Analysis).

[FIELD-TABLE]

| שדה                     | ערך            |
| ----------------------- | -------------- |
| שם הפרויקט / לקוח        | [שם הלקוח]      |
| מזהה משימה              | [מזהה]         |
| מחבר המסמך              | [שם הכותב]     |
| סביבת פיתוח (Sandbox)   | [שם סביבה]     |
| תאריך עדכון             | [DD/MM/YYYY]   |

[PAGEBREAK]

## 1. רקע עסקי ותקציר הפתרון הטכני

**הבעיה / הדרישה העסקית:** [הסבר קצר בעברית]
**הפתרון הטכני ברמת High Level:** [תיאור טכני קצר]

## 2. ניתוח הפתרון והחלטת OOTB מול Customization

**סוג הפתרון:** [OOTB (Declarative) / Customization (Apex / LWC)]
**נימוק:** [מדוע נבחר. אם Customization — מדוע OOTB בלתי אפשרי, בהתאם למנדט OOTB-First]

## 3. ERD — דיאגרמת ישויות

הפרדה בין ישויות Standard (OOTB) לישויות Custom המעורבות בתהליך, והיחסים ביניהן.

### 3.1 ישויות Standard (OOTB)

| Object Name | API Name | תפקיד בתהליך |
| ----------- | -------- | ------------ |
| [Object]    | [ApiName] | [הסבר בעברית] |

### 3.2 ישויות Custom

| Object Name | API Name | תפקיד בתהליך |
| ----------- | -------- | ------------ |
| [Object]    | [ApiName__c] | [הסבר בעברית] |

### 3.3 יחסים בין הישויות (ERD)

```text
[Standard: Account] 1 ──< [Custom: Protocol__c] (Master-Detail)
                                  │
                                  └──< [Custom: ChildItem__c] (Lookup)
```

## 4. מבנה נתונים וישויות (Data Model)

פירוט ברמת השדות של האובייקטים הרלוונטיים לתהליך.

| Object Name | API Name | Relationship | Purpose / הסבר |
| ----------- | -------- | ------------ | -------------- |
| [Object]    | [ApiName__c] | [-]      | [הסבר בעברית]  |

### 4.1 שינויים שבוצעו וההשפעה

טבלת הרכיבים ששונו/נוספו והשפעתם על תהליכים וישויות.

| # | רכיב | סוג | שונה בפועל? | מה עשינו / ההשפעה | ישויות מושפעות |
| - | ---- | --- | ----------- | ----------------- | -------------- |
| 1 | [ComponentName.cls] | [Apex Class] | [כן / לא / נפרס אוטומטית] | [מה בוצע וההשפעה — בעברית] | [ישויות מושפעות] |

## 5. אוטומציות ולוגיקה (Automation & Logic)

מעדיפים אוטומציה דקלרטיבית על קוד (OOTB-First). כל אוטומציה מקבלת תת-פרק משלה,
שכותרתו כוללת את **הסוג** ואת השם, ופורמט מותאם לסוג.

טבלת ריכוז כלל האוטומציות:

| # | סוג (Type) | שם (API Name) | Trigger / Timing | Purpose / הסבר |
| - | ---------- | ------------- | ---------------- | -------------- |
| 1 | [Screen Flow / OmniScript / Record-Triggered Flow / Scheduled Flow / Autolaunched Flow / Platform Event Flow / FlexCard / Quick Action / Apex] | [ApiName] | [מתי רץ] | [הסבר בעברית] |

[REPEAT: תת-פרק אחד לכל אוטומציה — בחרו פורמט לפי הסוג מבין הדפוסים הבאים]

### 5.N [Screen Flow / OmniScript] — [שם האוטומציה]

**מטרה:** [הסבר בעברית]
**הפעלה / טריגר:** [כפתור ב-List View / Record Page / ...]
**Record Type / קונטקסט:** [אם רלוונטי]
**מסכים ושדות:**
- [שם מסך]: שדות [FieldLabel (API)], ברירות מחדל [...], נראות/ולידציה [...]
**לוגיקה:** [תיאור בעברית]
**תוצאה (Create / Update):** [Object.Field (API) + הערכים שנקבעים]

### 5.N [Flow — Record-Triggered / Scheduled / Autolaunched / Platform Event] — [שם]

**סוג ה-Flow:** [Record-Triggered (before-save / after-save / async) / Scheduled / Autolaunched (No Trigger) / Platform Event-Triggered]
**מקור הפעלה:** [Object + Create/Update/Delete · או לוח זמנים · או שם ה-Platform Event · או מי שקורא ל-Autolaunched]
**קריטריון כניסה:** [תנאי בעברית]
**פעולות:** [Create/Update/Delete — Object.Field (API) + ערכים · שליחת Email/Event · קריאת Subflow]
**הצדקת OOTB-First:** [מדוע Flow ולא קוד]

### 5.N [FlexCard] — [שם]

**מקור נתונים (Data Source):** [Object / SOQL]
**עמודות תצוגה:**

| עמודה | מקור (Field API) | קליקבילי? | הערות |
| ----- | ---------------- | --------- | ----- |
| [עמודה] | [Object.Field__c] | [כן/לא] | [הערה בעברית] |

**פעולות / כפתורים:** [שם כפתור → מה הוא עושה + Flow/Action מופעל]
**תצוגות מקוננות (Collapse):** [Object + שדות מוצגים]

### 5.N [Quick Action / Button] — [שם]

**מיקום:** [Object / Layout / List View]
**שדות במסך:** [FieldLabel (API) — מקור / ברירת מחדל / אוט' מאוכלס]
**לוגיקה / Flow שמופעל:** [שם ה-Flow + מה הוא מבצע — למשל יצירת Funding_Award__c]

### 5.N [Apex — Trigger / Class / Batch / Queueable / Scheduled] — [שם]

**סוג:** [Apex Trigger / Class / Batch / Queueable / Scheduled]
**אובייקט / הקשר:** [Object + before/after אם Trigger]
**מתי רץ / מי מפעיל:** [תיאור בעברית]
**לוגיקה עיקרית:** [תיאור בעברית]
**הצדקת OOTB-First:** [מדוע נדרש קוד ולא פתרון דקלרטיבי — חובה]

## 6. טפסים (Forms — OmniStudio / LWC)

מוצג רק אם קיימים טפסים באפיון (אחרת: "לא רלוונטי"). כל טופס מקבל תת-פרק משלו.
טופס יכול להיות ממומש כ-**OmniStudio (OmniScript)** או כ-**Custom LWC**.

[REPEAT: תת-פרק אחד לכל טופס]

### 6.N טופס [שם הטופס] — אפיון טכני

**מימוש (Implementation):** [OmniStudio OmniScript / Custom LWC]
**רכיבים טכניים:** [שם ה-OmniScript · או שם ה-LWC + Apex Controller (API) · DataRaptor / Integration Procedure אם רלוונטי]
**ממשקי נתונים (במימוש LWC):** [@wire / imperative Apex methods · Events · @api properties — אם Custom LWC]
**הנחת יישום:** [הסבר בעברית]
**אופן הפעלה:**
- [שלב 1 — למשל: כניסה לרשומת Budget ולחיצה על כפתור "הקמת מענק" הקורא לטופס]

[REPEAT: תת-תת-פרק אחד לכל מסך/שלב בטופס]

#### שם מסך: [שם המסך]

| FrontEnd | דוגמא לערכים | BackEnd |
| -------- | ------------ | ------- |
| [שדה / תווית במסך] | [ערך לדוגמה] | [Object.Field (API) + הערות מיפוי בעברית] |

## 7. זרימת המידע (Data Flow)

תיאור מסלול המידע מקצה לקצה בין הרכיבים. הדיאגרמה ב-LTR / monospace.

```text
[Config LWC: componentName]
   admin action --> saved config
        |
        v
[Runtime LWC: componentName]
   sends data --> Apex
        |
        v
[Apex: ControllerName.method]   <== single expansion point
   process -> transform -> query
        |
        v
[Runtime LWC: componentName]  renders result
```

## 8. מגבלות פלטפורמה ו-Governor Limits

**מגבלות רלוונטיות שאומתו מול תיעוד רשמי:** [פירוט בעברית + מספרים/מונחים באנגלית]

## 9. מקרי בדיקה QA

### 9.1 Positive

- [תנאי הבדיקה בעברית] ← [התוצאה הצפויה]

### 9.2 Negative

- [תנאי הבדיקה בעברית] ← [התוצאה הצפויה]

### 9.3 Regression

- [תנאי הבדיקה בעברית] ← [התוצאה הצפויה]

## 10. סיכונים ונקודות לתחקור עתידי

- [נקודת סיכון / הנחה לא-טריוויאלית / נושא לתחקור עתידי — בעברית]

## 11. הנחות ושאלות פתוחות

**הנחות:** [רשימה בעברית]
**שאלות פתוחות:** [רשימה בעברית]

## 12. נספח — מקורות תיעוד

**מקורות רשמיים שנעשה בהם שימוש:** [קישורים ל-help.salesforce.com / developer.salesforce.com]
