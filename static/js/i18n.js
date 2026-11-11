(function () {
  var STORAGE_KEY = "site_lang";

  var T = {
    /* Header / nav */
    nav_home: { en: "Home", mr: "मुख्यपृष्ठ" },
    nav_properties: { en: "All Properties", mr: "सर्व मालमत्ता" },
    nav_about: { en: "About / Contact", mr: "आमच्याबद्दल / संपर्क" },
    nav_interests: { en: "My Interests", mr: "माझी आवड" },
    nav_logout: { en: "Logout", mr: "बाहेर पडा" },
    nav_login: { en: "Login", mr: "लॉगिन" },
    nav_call: { en: "📞 Call Now", mr: "📞 आता कॉल करा" },
    brand_tag: { en: "Real Estate · Vidarbha", mr: "रियल इस्टेट · विदर्भ" },
    open_menu: { en: "Open menu", mr: "मेनू उघडा" },

    /* Footer */
    footer_phone: { en: "Phone:", mr: "फोन:" },
    footer_whatsapp: { en: "WhatsApp", mr: "व्हॉट्सॲप" },
    footer_note: {
      en: "Browse freely. Login only when you click “I’m Interested”.",
      mr: "मुक्तपणे ब्राउझ करा. “मला आवडते” क्लिक केल्यावरच लॉगिन करा.",
    },

    /* Home */
    hero_eyebrow: {
      en: "Trusted local broker · Vidarbha, Maharashtra",
      mr: "विश्वासू स्थानिक दलाल · विदर्भ, महाराष्ट्र",
    },
    hero_desc: {
      en: "Find plots, flats, houses & farms. Call anytime — no login needed to browse.",
      mr: "प्लॉट, फ्लॅट, घर व शेत जमीन शोधा. कधीही कॉल करा — ब्राउझ करण्यासाठी लॉगिनची गरज नाही.",
    },
    hero_real_estate: {
      en: "Real Estate — Vidarbha",
      mr: "रियल इस्टेट — विदर्भ",
    },
    hero_see_all: { en: "See all properties", mr: "सर्व मालमत्ता पहा" },
    featured_title: { en: "Featured properties", mr: "विशेष मालमत्ता" },
    featured_sub: { en: "Hand-picked listings in Vidarbha", mr: "विदर्भातील निवडक यादी" },
    latest_title: { en: "Latest properties", mr: "नवीनतम मालमत्ता" },
    latest_sub: { en: "Newly added across Vidarbha", mr: "विदर्भभर नवीन जोडलेल्या" },
    view_all: { en: "View all", mr: "सर्व पहा" },
    empty_no_props: { en: "No properties yet.", mr: "अद्याप मालमत्ता नाहीत." },
    empty_ask_broker: {
      en: "Ask the broker to add listings from the dashboard.",
      mr: "डॅशबोर्डमधून यादी जोडण्यासाठी दलालाला सांगा.",
    },
    call_now: { en: "Call now", mr: "आता कॉल करा" },

    /* List / filters */
    list_title: { en: "All properties", mr: "सर्व मालमत्ता" },
    list_sub: { en: "Vidarbha properties · Browse freely", mr: "विदर्भ मालमत्ता · मुक्तपणे ब्राउझ करा" },
    show_filters: { en: "🔍 Show filters", mr: "🔍 फिल्टर दाखवा" },
    label_search: { en: "Search", mr: "शोधा" },
    ph_search: { en: "Society, road, keyword", mr: "सोसायटी, रस्ता, कीवर्ड" },
    label_area: { en: "Area", mr: "क्षेत्र" },
    all_areas: { en: "All areas", mr: "सर्व क्षेत्रे" },
    label_type: { en: "Property type", mr: "मालमत्तेचा प्रकार" },
    all_types: { en: "All types", mr: "सर्व प्रकार" },
    label_status: { en: "Status", mr: "स्थिती" },
    any_status: { en: "Any status", mr: "कोणतीही स्थिती" },
    label_min_price: { en: "Min price (₹)", mr: "किमान किंमत (₹)" },
    label_max_price: { en: "Max price (₹)", mr: "कमाल किंमत (₹)" },
    apply_filters: { en: "Apply filters", mr: "फिल्टर लागू करा" },
    clear: { en: "Clear", mr: "साफ करा" },
    empty_no_match: { en: "No properties match your filters.", mr: "तुमच्या फिल्टरशी जुळणाऱ्या मालमत्ता नाहीत." },
    empty_try_clear: {
      en: "Try clearing filters or call the broker for help.",
      mr: "फिल्टर साफ करा किंवा मदतीसाठी दलालाला कॉल करा.",
    },
    call_broker: { en: "📞 Call broker", mr: "📞 दलालाला कॉल करा" },

    /* Card / detail */
    view_details: { en: "View details", mr: "तपशील पहा" },
    sq_ft: { en: "sq ft", mr: "चौ. फूट" },
    acres: { en: "acres", mr: "एकर" },
    bhk: { en: "BHK", mr: "बीएचके" },
    per_sq_ft: { en: "/ sq ft", mr: "/ चौ. फूट" },
    total_price: { en: "Price", mr: "किंमत" },
    price_sqft: { en: "Price / sq ft", mr: "किंमत / चौ. फूट" },
    call_for_price: { en: "Call for price", mr: "किंमतीसाठी कॉल करा" },
    ask_broker: { en: "Ask broker on call / WhatsApp", mr: "कॉल / व्हॉट्सॲपवर विचारा" },
    area_label: { en: "Area", mr: "क्षेत्रफळ" },
    type_label: { en: "Type", mr: "प्रकार" },
    open_maps: { en: "🗺 Open in Google Maps", mr: "🗺 Google Maps मध्ये उघडा" },
    property_video: { en: "Property video", mr: "मालमत्तेचा व्हिडिओ" },
    details: { en: "Details", mr: "तपशील" },
    detail_tip: {
      en: "No login needed to call or WhatsApp. Login is only for “I’m Interested”.",
      mr: "कॉल किंवा व्हॉट्सॲपसाठी लॉगिनची गरज नाही. “मला आवडते” साठीच लॉगिन.",
    },
    call: { en: "📞 Call", mr: "📞 कॉल" },
    whatsapp: { en: "WhatsApp", mr: "व्हॉट्सॲप" },
    im_interested: { en: "I’m Interested", mr: "मला आवडते" },
    interest_sent: { en: "Interest Sent ✔", mr: "आवड पाठवली ✔" },
    sold: { en: "Sold", mr: "विकली" },
    share_wa: { en: "↗ Share on WhatsApp", mr: "↗ व्हॉट्सॲपवर शेअर करा" },
    no_photo: { en: "No photo", mr: "फोटो नाही" },

    /* Statuses / types */
    status_available: { en: "Available", mr: "उपलब्ध" },
    status_under_negotiation: { en: "Under Negotiation", mr: "वाटाघाटी सुरू" },
    status_sold: { en: "Sold", mr: "विकली" },
    type_plot: { en: "Plot", mr: "प्लॉट" },
    type_flat: { en: "Flat", mr: "फ्लॅट" },
    type_house: { en: "House", mr: "घर" },
    type_shop: { en: "Shop", mr: "दुकान" },
    type_farm: { en: "Farm", mr: "शेत" },
    type_other: { en: "Other", mr: "इतर" },

    /* About */
    about_body1: {
      en: "We help families find plots, flats, houses, shops and farms with clear photos and area (sq ft). Call or WhatsApp for price.",
      mr: "आम्ही कुटुंबांना स्पष्ट फोटो व क्षेत्रफळ (चौ. फूट) सह प्लॉट, फ्लॅट, घर, दुकान व शेत शोधण्यास मदत करतो. किंमतीसाठी कॉल किंवा व्हॉट्सॲप करा.",
    },
    about_body2: {
      en: "You can browse the full website without registering. When you like a property, tap I’m Interested — register or login with mobile and password, then we can call you.",
      mr: "नोंदणी न करता संपूर्ण वेबसाइट ब्राउझ करू शकता. मालमत्ता आवडल्यास “मला आवडते” टॅप करा — मोबाइल व पासवर्डने नोंदणी/लॉगिन करा, नंतर आम्ही कॉल करू शकतो.",
    },
    chat_wa: { en: "Chat on WhatsApp", mr: "व्हॉट्सॲपवर चॅट करा" },
    see_properties: { en: "See properties", mr: "मालमत्ता पहा" },
    about_serving: {
      en: "Serving Nagpur, Amravati, Akola, Yavatmal, Wardha, Chandrapur, Bhandara, Gondia, Washim and all Vidarbha.",
      mr: "नागपूर, अमरावती, अकोला, यवतमाळ, वर्धा, चंद्रपूर, भंडारा, गोंदिया, वाशिम व संपूर्ण विदर्भात सेवा.",
    },
    broker_login: { en: "Broker login", mr: "दलाल लॉगिन" },
    broker_only: { en: "(for property owner only)", mr: "(फक्त मालमत्ता मालकासाठी)" },

    /* My interests */
    interests_title: { en: "My interested properties", mr: "माझ्या आवडीच्या मालमत्ता" },
    interests_sub: {
      en: "The broker has your number for these listings",
      mr: "या यादीसाठी दलालाकडे तुमचा क्रमांक आहे",
    },
    open_property: { en: "Open property", mr: "मालमत्ता उघडा" },
    empty_no_interest: {
      en: "You have not marked any property yet.",
      mr: "तुम्ही अद्याप कोणतीही मालमत्ता निवडलेली नाही.",
    },
    empty_tap_interest: {
      en: "Open a property and tap “I’m Interested”.",
      mr: "मालमत्ता उघडा आणि “मला आवडते” टॅप करा.",
    },
    browse_properties: { en: "Browse properties", mr: "मालमत्ता ब्राउझ करा" },

    /* Interest sent page */
    interest_saved_title: { en: "Interest saved ✔", mr: "आवड जतन झाली ✔" },
    label_property: { en: "Property:", mr: "मालमत्ता:" },
    interest_saved_hint: {
      en: "Tap the button below once, then tap Send in WhatsApp. (Only this one property will be in the message.)",
      mr: "खालील बटण एकदाच टॅप करा, नंतर व्हॉट्सॲपमध्ये पाठवा टॅप करा. (संदेशात फक्त ही एक मालमत्ता असेल.)",
    },
    send_interest_wa: {
      en: "Send interest on WhatsApp",
      mr: "व्हॉट्सॲपवर आवड पाठवा",
    },
    my_interested_props: {
      en: "My interested properties",
      mr: "माझ्या आवडीच्या मालमत्ता",
    },
    browse_more_props: {
      en: "Browse more properties",
      mr: "आणखी मालमत्ता ब्राउझ करा",
    },

    /* Auth */
    login_title: { en: "Login", mr: "लॉगिन" },
    login_hint: {
      en: "Enter your mobile number and password.",
      mr: "मोबाइल क्रमांक व पासवर्ड टाका.",
    },
    label_phone: { en: "Mobile number", mr: "मोबाइल क्रमांक" },
    ph_phone: { en: "10-digit number", mr: "१० अंकी क्रमांक" },
    label_password: { en: "Password", mr: "पासवर्ड" },
    label_password2: { en: "Confirm password", mr: "पासवर्ड पुन्हा टाका" },
    ph_password: { en: "Strong password", mr: "मजबूत पासवर्ड" },
    ph_password2: { en: "Enter password again", mr: "पासवर्ड पुन्हा टाका" },
    show_password: { en: "Show password", mr: "पासवर्ड दाखवा" },
    hide_password: { en: "Hide password", mr: "पासवर्ड लपवा" },
    pw_len: { en: "At least 8 characters", mr: "किमान ८ अक्षरे" },
    pw_upper: { en: "One uppercase letter (A–Z)", mr: "एक मोठे अक्षर (A–Z)" },
    pw_lower: { en: "One lowercase letter (a–z)", mr: "एक लहान अक्षर (a–z)" },
    pw_digit: { en: "One number (0–9)", mr: "एक अंक (0–9)" },
    pw_special: { en: "One special character (!@#$)", mr: "एक खास चिन्ह (!@#$)" },
    pw_match: { en: "Both passwords match", mr: "दोन्ही पासवर्ड सारखे" },
    ph_password_login: { en: "Your password", mr: "तुमचा पासवर्ड" },
    btn_login: { en: "Login", mr: "लॉगिन" },
    btn_register: { en: "Create account", mr: "खाते तयार करा" },
    new_user: { en: "New user?", mr: "नवीन वापरकर्ता?" },
    register_here: { en: "Register here", mr: "येथे नोंदणी करा" },

    register_title: { en: "Register", mr: "नोंदणी" },
    register_hint: {
      en: "Enter your name, mobile number and a password.",
      mr: "नाव, मोबाइल क्रमांक व पासवर्ड टाका.",
    },
    label_name: { en: "Your full name", mr: "तुमचे पूर्ण नाव" },
    ph_name: { en: "e.g. Ramesh Patil", mr: "उदा. रमेश पाटील" },
    already_reg: { en: "Already registered?", mr: "आधीच नोंदणी केली आहे?" },
    login_here: { en: "Login here", mr: "येथे लॉगिन करा" },

    auth_almost: { en: "Almost done", mr: "जवळजवळ पूर्ण" },
    auth_hint: {
      en: "To send “I’m Interested” to the broker, please register or login with your mobile number and password.",
      mr: "दलालाला “मला आवडते” पाठवण्यासाठी मोबाइल व पासवर्डने नोंदणी किंवा लॉगिन करा.",
    },
    auth_register: { en: "New here — Register", mr: "नवीन आहात — नोंदणी करा" },
    auth_login: { en: "Already registered — Login", mr: "आधीच नोंदणी — लॉगिन" },
    auth_back: { en: "Go back", mr: "मागे जा" },
    auth_tip: {
      en: "Large buttons · Mobile + password · Easy for everyone",
      mr: "मोठी बटणे · मोबाइल + पासवर्ड · सर्वांसाठी सोपे",
    },
  };

  function getLang() {
    var saved = localStorage.getItem(STORAGE_KEY);
    if (saved === "mr" || saved === "en") return saved;
    return "en";
  }

  function setLang(lang) {
    if (lang !== "en" && lang !== "mr") lang = "en";
    localStorage.setItem(STORAGE_KEY, lang);
    applyLang(lang);
  }

  function textFor(key, lang) {
    var entry = T[key];
    if (!entry) return null;
    return entry[lang] || entry.en || null;
  }

  function applyLang(lang) {
    document.documentElement.lang = lang === "mr" ? "mr" : "en";
    document.documentElement.setAttribute("data-lang", lang);

    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      var key = el.getAttribute("data-i18n");
      var val = textFor(key, lang);
      if (val == null) return;
      el.textContent = val;
    });

    document.querySelectorAll("[data-i18n-html]").forEach(function (el) {
      var key = el.getAttribute("data-i18n-html");
      var val = textFor(key, lang);
      if (val == null) return;
      el.innerHTML = val;
    });

    document.querySelectorAll("[data-i18n-placeholder]").forEach(function (el) {
      var key = el.getAttribute("data-i18n-placeholder");
      var val = textFor(key, lang);
      if (val == null) return;
      el.setAttribute("placeholder", val);
    });

    document.querySelectorAll("[data-i18n-aria]").forEach(function (el) {
      var key = el.getAttribute("data-i18n-aria");
      var val = textFor(key, lang);
      if (val == null) return;
      el.setAttribute("aria-label", val);
    });

    document.querySelectorAll(".lang-btn").forEach(function (btn) {
      var active = btn.getAttribute("data-lang") === lang;
      btn.classList.toggle("active", active);
      btn.setAttribute("aria-pressed", active ? "true" : "false");
    });
  }

  function init() {
    var switcher = document.getElementById("langSwitch");
    if (switcher) {
      switcher.addEventListener("click", function (e) {
        var btn = e.target.closest(".lang-btn");
        if (!btn) return;
        setLang(btn.getAttribute("data-lang"));
      });
    }
    applyLang(getLang());
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  window.SiteI18n = { setLang: setLang, getLang: getLang, applyLang: applyLang, textFor: textFor };
})();
