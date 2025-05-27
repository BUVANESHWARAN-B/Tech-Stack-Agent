# rules_engine.py
def apply_pre_checks(project_details):
    """
    Applies a set of predefined rules to the project details.
    Returns a direct recommendation, an error message, or None if no rule triggers.
    """
    app_type = project_details.get("app_type", "").lower()
    description = project_details.get("project_description", "").lower()
    scalability = project_details.get("scalability_needs", "").lower()
    budget = project_details.get("budget", "").lower()
    timeline = project_details.get("timeline", "").lower()
    team_skills = [skill.lower() for skill in project_details.get("team_skills", [])]

    # Rule 1: Simple Static Site
    static_site_keywords = ["static site", "brochure website", "portfolio", "landing page"]
    if any(keyword in app_type or keyword in description for keyword in static_site_keywords) and \
       scalability in ["low", ""] and budget == "low" and timeline.startswith("very short"):
        return {
            "recommendations": [{
                "stack_name": "JAMstack (e.g., Astro / Eleventy / Hugo / Next.js static export)",
                "core_components": ["Static Site Generator", "CDN (Netlify, Vercel, GitHub Pages)"],
                "justification": "For simple, static content with low budget and fast timeline, JAMstack offers optimal performance, security, and low cost.",
                "pros": ["Excellent performance", "High security", "Low hosting costs", "Good developer experience"],
                "cons": ["Not suitable for dynamic server-side logic without workarounds (serverless functions)", "Build times can increase for very large sites"]
            }],
            "source": "Rule-Based Pre-check"
        }

    # Rule 2: Contradiction - High Scalability with No Backend
    if scalability in ["high", "very high"] and ("no backend" in description or "frontend only" in app_type or not any(skill in ["node.js", "python", "java", "go", "ruby", "php", "c#"] for skill in team_skills if "none" not in team_skills)):
        return {
            "error": "Contradictory Input",
            "details": "High scalability typically requires a robust backend. Please clarify if a backend is needed or adjust scalability expectations.",
            "source": "Rule-Based Pre-check"
        }

    # Rule 3: Contradiction - Complex Project, Short Timeline, Low Expertise/Budget
    complex_keywords = ["enterprise system", "large scale platform", "many complex features"]
    if any(keyword in description for keyword in complex_keywords) and \
       timeline.startswith(("very short", "short")) and \
       (budget == "low" or "none" in team_skills or not team_skills):
        return {
            "error": "Potentially Unrealistic Scope",
            "details": "A complex project with a very short timeline and limited budget/expertise is challenging. Consider adjusting scope, timeline, or budget.",
            "source": "Rule-Based Pre-check"
        }

    return None # No rule triggered, proceed to LLM