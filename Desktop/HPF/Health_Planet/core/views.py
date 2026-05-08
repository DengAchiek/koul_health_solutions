from django.shortcuts import render


PROJECTS = [
    {
        "title": "Climate-Smart Clinics",
        "description": "Helping rural health posts prepare for heat, flooding, and service disruption through local planning and practical resilience tools.",
        "status": "Active",
    },
    {
        "title": "Safe Motherhood Circles",
        "description": "Community-led sessions connecting expectant mothers with health information, referral support, and trusted peer networks.",
        "status": "Field program",
    },
    {
        "title": "Youth Mental Wellness",
        "description": "School and community outreach that makes mental health conversations easier, earlier, and connected to local care pathways.",
        "status": "Growing",
    },
]

NEWS_ITEMS = [
    {
        "title": "Community health volunteers expand outreach in Lusaka Province",
        "date": "May 2026",
        "summary": "New volunteer cohorts are supporting health talks, referrals, and preparedness conversations in high-risk communities.",
    },
    {
        "title": "Climate resilience sessions reach district health teams",
        "date": "April 2026",
        "summary": "District teams reviewed practical response plans for heat stress, water safety, and continuity of essential services.",
    },
    {
        "title": "Youth wellness clubs launch a peer-support calendar",
        "date": "March 2026",
        "summary": "Young leaders are creating consistent spaces for mental wellness education and early help-seeking.",
    },
]

CAREER_OPENINGS = [
    {
        "role": "Community Programs Coordinator",
        "location": "Lusaka, Zambia",
        "type": "Full time",
    },
    {
        "role": "Monitoring and Learning Assistant",
        "location": "Hybrid",
        "type": "Contract",
    },
]

INTERNSHIPS = [
    {
        "role": "Communications Intern",
        "focus": "Storytelling, campaigns, and partner updates",
    },
    {
        "role": "Public Health Intern",
        "focus": "Field research, community sessions, and reporting support",
    },
]


def home(request):
    context = {
        "projects": PROJECTS,
        "news_items": NEWS_ITEMS[:2],
    }
    return render(request, "home.html", context)


def about(request):
    return render(request, "about.html")


def projects(request):
    return render(request, "projects.html", {"projects": PROJECTS})


def news(request):
    return render(request, "news.html", {"news_items": NEWS_ITEMS})


def careers(request):
    return render(request, "careers.html", {"openings": CAREER_OPENINGS})


def internships(request):
    return render(request, "internships.html", {"internships": INTERNSHIPS})


def donate(request):
    context = {"submitted": request.method == "POST"}
    return render(request, "donate.html", context)


def contact(request):
    context = {"submitted": request.method == "POST"}
    return render(request, "contact.html", context)
