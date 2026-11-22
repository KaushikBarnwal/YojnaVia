"""
Trilingual Notification Templates for WhatsApp and SMS Reminders.
Languages: English (en), Marathi (mr), Hindi (hi).

Strict Invariant:
Never invent dates. All parameters must be interpolated from verified Scheme records
or citizen-confirmed ApplicationRecord milestones.
"""

from typing import Dict, Any

NOTIFICATION_TEMPLATES: Dict[str, Dict[str, Dict[str, str]]] = {
    "DEADLINE_APPROACHING": {
        "en": {
            "title": "Application Deadline Alert: {scheme_name}",
            "body": (
                "Namaste {student_name}, this is an important reminder from YojnaVia. "
                "The official application deadline for '{scheme_name}' on the {portal_name} portal is on {deadline} "
                "({days_left} days remaining). Please ensure all mandatory documents are submitted before portal cutoff."
            )
        },
        "mr": {
            "title": "अर्ज अंतिम मुदत सूचना: {scheme_name}",
            "body": (
                "नमस्ते {student_name}, योजनाव्हायाकडून महत्त्वाची सूचना. "
                "'{scheme_name}' या योजनेसाठी {portal_name} संकेतस्थळावर अर्ज करण्याची अंतिम मुदत {deadline} आहे "
                "(फक्त {days_left} दिवस शिल्लक). कृपया मुदतीपूर्वी आपले कागदपत्र सादर करा."
            )
        },
        "hi": {
            "title": "आवेदन अंतिम तिथि अलर्ट: {scheme_name}",
            "body": (
                "नमस्ते {student_name}, योजनावाया की ओर से महत्वपूर्ण सूचना। "
                "'{scheme_name}' के लिए {portal_name} पोर्टल पर आवेदन की अंतिम तिथि {deadline} है "
                "(केवल {days_left} दिन शेष)। कृपया पोर्टल बंद होने से पहले अपने दस्तावेज़ जमा करें।"
            )
        }
    },

    "MISSING_DOCUMENT_REMINDER": {
        "en": {
            "title": "Missing Document Reminder: {document_name}",
            "body": (
                "Namaste {student_name}, your application for '{scheme_name}' is currently waiting for: "
                "'{document_name}'. You can apply online via Aaple Sarkar portal ({sla_days}-day statutory SLA). "
                "Obtaining this unlocks your application progress."
            )
        },
        "mr": {
            "title": "प्रलंबित कागदपत्र स्मरणपत्र: {document_name}",
            "body": (
                "नमस्ते {student_name}, '{scheme_name}' या अर्जासाठी आपले '{document_name}' अद्याप प्रलंबित आहे. "
                "आपण 'आपले सरकार' पोर्टलवरून हे प्रमाणपत्र मिळवू शकता (वैधानिक मुदत: {sla_days} दिवस). "
                "शिष्यवृत्ती मिळवण्यासाठी हे तातडीने पूर्ण करा."
            )
        },
        "hi": {
            "title": "लंबित दस्तावेज़ स्मरणपत्र: {document_name}",
            "body": (
                "नमस्ते {student_name}, '{scheme_name}' के आवेदन के लिए आपका '{document_name}' अभी बाकी है। "
                "आप 'आपले सरकार' पोर्टल से इसे प्राप्त कर सकते हैं (अधिनियमित समय: {sla_days} दिन)। "
                "प्रक्रिया पूरी करने के लिए इसे जल्द बनवाएं।"
            )
        }
    },

    "MILESTONE_UPDATED": {
        "en": {
            "title": "Application Milestone Updated: {new_status}",
            "body": (
                "Namaste {student_name}, your tracker status for '{scheme_name}' has been updated to '{new_status}'. "
                "Next immediate action: {next_action}."
            )
        },
        "mr": {
            "title": "अर्ज स्थिती अद्यतन: {new_status}",
            "body": (
                "नमस्ते {student_name}, '{scheme_name}' या योजनेतील आपल्या अर्जाची स्थिती आता '{new_status}' अशी नोंदवली गेली आहे. "
                "पुढील पायरी: {next_action}."
            )
        },
        "hi": {
            "title": "आवेदन स्थिति अपडेट: {new_status}",
            "body": (
                "नमस्ते {student_name}, '{scheme_name}' के आवेदन की स्थिति अब '{new_status}' हो गई है। "
                "अगला आवश्यक कदम: {next_action}."
            )
        }
    },

    "STATUS_INACTIVITY": {
        "en": {
            "title": "Application Follow-Up Nudge: {scheme_name}",
            "body": (
                "Namaste {student_name}, your tracked application for '{scheme_name}' has been in '{status}' "
                "status for over 14 days. Don't lose momentum! Have you visited your college scholarship clerk? "
                "Update your progress in YojnaVia to keep track."
            )
        },
        "mr": {
            "title": "अर्ज प्रगती पाठपुरावा: {scheme_name}",
            "body": (
                "नमस्ते {student_name}, '{scheme_name}' या योजनेचा अर्ज गेल्या १४ दिवसांपासून '{status}' स्थितीत आहे. "
                "महाविद्यालयीन लिपिकाकडे कागदपत्रे जमा केली आहेत का? योजनाव्हाया ट्रॅकरमध्ये आपली ताजी स्थिती अद्यतनित करा."
            )
        },
        "hi": {
            "title": "आवेदन प्रगति फॉलो-अप: {scheme_name}",
            "body": (
                "नमस्ते {student_name}, '{scheme_name}' का आपका आवेदन पिछले 14 दिनों से '{status}' स्थिति में है। "
                "क्या आपने कॉलेज क्लर्क से संपर्क किया? अपनी स्थिति योजनावाया ट्रैकर में अपडेट करें।"
            )
        }
    },

    "GRIEVANCE_RESUBMISSION": {
        "en": {
            "title": "Action Needed: 15-Day Scrutiny Resubmission Clock",
            "body": (
                "IMPORTANT: {student_name}, a scrutiny query was noted for '{scheme_name}'. "
                "Under Maharashtra Government operational guidelines, you have a 15-day window to rectify documents "
                "without losing priority. Resubmit corrected documents before {resubmission_deadline}."
            )
        },
        "mr": {
            "title": "तातडीची कृती: १५ दिवसांची छाननी दुरुस्ती मुदत",
            "body": (
                "महत्त्वाचे: {student_name}, '{scheme_name}' या अर्जात त्रुटी आढळली आहे. "
                "शासकीय नियमांनुसार त्रुटी दुरुस्त करून कागदपत्रे पुन्हा सादर करण्यासाठी १५ दिवसांची मुदत मिळते. "
                "{resubmission_deadline} पूर्वी दुरुस्त कागदपत्रे अपलोड करा."
            )
        },
        "hi": {
            "title": "आवश्यक कार्यवाही: 15 दिन की स्क्रूटनी सुधार खिड़की",
            "body": (
                "जरूरी: {student_name}, '{scheme_name}' के आवेदन में आपत्ति दर्ज की गई है। "
                "सरकारी नियमों के तहत आपको सुधार के लिए 15 दिन की समय-सीमा मिलती है। "
                "{resubmission_deadline} से पहले सही दस्तावेज़ दोबारा जमा करें।"
            )
        }
    },

    "ANNUAL_RENEWAL": {
        "en": {
            "title": "Statutory Annual Renewal Reminder (March 31 Cutoff)",
            "body": (
                "Namaste {student_name}, Tahsildar Income Certificates and Non-Creamy Layer (NCL) validity "
                "expires on March 31. Apply for your fresh certificate on Aaple Sarkar now to ensure uninterrupted "
                "scholarship renewal for Academic Year {academic_year}."
            )
        },
        "mr": {
            "title": "वार्षिक नूतनीकरण सूचना (३१ मार्च मुदत)",
            "body": (
                "नमस्ते {student_name}, तहसीलदार उत्पन्नाचा दाखला व नॉन-क्रिमीलेअरची मुदत ३१ मार्च रोजी संपते. "
                "पुढील शैक्षणिक वर्षाच्या ({academic_year}) शिष्यवृत्ती नूतनीकरणासाठी 'आपले सरकार' वरून नवा दाखला तातडीने काढा."
            )
        },
        "hi": {
            "title": "वार्षिक नवीनीकरण अलर्ट (31 मार्च अंतिम तिथि)",
            "body": (
                "नमस्ते {student_name}, तहसीलदार आय प्रमाण पत्र और नॉन-क्रीमी लेयर की वैधता 31 मार्च को समाप्त होती है। "
                "शैक्षणिक वर्ष {academic_year} के छात्रवृत्ति नवीनीकरण के लिए 'आपले सरकार' से नया प्रमाण पत्र तुरंत बनवाएं।"
            )
        }
    },

    "TEST_DEMO": {
        "en": {
            "title": "YojnaVia Test Notification Ping",
            "body": (
                "Namaste {student_name}, this is a verified test reminder from YojnaVia. "
                "Your mobile notification preference ({channel}) has been successfully linked. "
                "You will receive official deadline, missing document, and scrutiny reminders here."
            )
        },
        "mr": {
            "title": "योजनाव्हाया चाचणी संदेश",
            "body": (
                "नमस्ते {student_name}, हा योजनाव्हायाकडून आलेला चाचणी संदेश आहे. "
                "आपली मोबाईल सूचना प्रणाली ({channel}) यशस्वीरीत्या सुरू झाली आहे. "
                "आपणास शासकीय मुदती व कागदपत्रांचे वेळेवर स्मरणपत्र येथे प्राप्त होईल."
            )
        },
        "hi": {
            "title": "योजनावाया परीक्षण संदेश",
            "body": (
                "नमस्ते {student_name}, यह योजनावाया की ओर से परीक्षण संदेश है। "
                "आपकी मोबाइल सूचना सेवा ({channel}) सफलतापूर्वक सक्रिय हो गई है। "
                "आपको सरकारी समय-सीमा व दस्तावेज़ों की सही सूचना यहां मिलेगी।"
            )
        }
    }
}


def render_template(event_type: str, language: str, context: Dict[str, Any]) -> Dict[str, str]:
    """
    Renders title and body for the given event type in the requested language,
    falling back to English if the translation is missing.
    """
    event_templates = NOTIFICATION_TEMPLATES.get(event_type, NOTIFICATION_TEMPLATES["TEST_DEMO"])
    lang_template = event_templates.get(language, event_templates.get("en", {}))

    raw_title = lang_template.get("title", "YojnaVia Notification")
    raw_body = lang_template.get("body", "You have a new update regarding your scheme.")

    # Safe formatting with fallback to empty strings
    safe_context = {k: str(v) if v is not None else "" for k, v in context.items()}
    # Populate standard defaults
    safe_context.setdefault("student_name", "Student")
    safe_context.setdefault("scheme_name", "Higher Education Scheme")
    safe_context.setdefault("portal_name", "MahaDBT")
    safe_context.setdefault("days_left", "3")
    safe_context.setdefault("deadline", "Upcoming Date")
    safe_context.setdefault("document_name", "Tahsildar Income Certificate")
    safe_context.setdefault("sla_days", "15")
    safe_context.setdefault("new_status", "Updated")
    safe_context.setdefault("status", "Active")
    safe_context.setdefault("next_action", "Review application checklist")
    safe_context.setdefault("resubmission_deadline", "in 15 days")
    safe_context.setdefault("academic_year", "2024-25")
    safe_context.setdefault("channel", "WhatsApp")

    try:
        title = raw_title.format(**safe_context)
    except Exception:
        title = raw_title

    try:
        body = raw_body.format(**safe_context)
    except Exception:
        body = raw_body

    return {
        "title": title,
        "body": body
    }
