import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Function to load data from JSON file
def load_data('data'):

    with open('data/employers.json', 'r') as file:
    employers_data = json.load(file)

    with open('data/candidates.json', 'r') as file:
    candidates_data = json.load(file)

        return json.load(file)


# Function to compute skills score: counts the matching skills
def compute_skills_score(job_skills, candidate_skills):
    common_skills = set(job_skills).intersection(set(candidate_skills))
    return len(common_skills) / len(job_skills)  # Return ratio of matched skills

# Function to compute location score (1 if same location, 0.5 if nearby, 0 otherwise)
def compute_location_score(job_location, candidate_location):
    if job_location in candidate_location:
        return 1
    else:
        return 0.5  # You can improve this based on more sophisticated location matching

# Function to compute salary score (1 if within the range, 0 otherwise)
def compute_salary_score(job_salary_range, candidate_salary_range):
    job_min, job_max = [int(s.split("₹")[1].split("/")[0].replace(",", "")) for s in job_salary_range.split("-")]
    candidate_min, candidate_max = [int(s.split("₹")[1].split("/")[0].replace(",", "")) for s in candidate_salary_range.split("-")]
    
    if job_min <= candidate_max and job_max >= candidate_min:
        return 1
    else:
        return 0

# Function to compute experience score (higher is better)
def compute_experience_score(job_experience, candidate_experience):
    job_years = int(job_experience.split()[0]) if 'year' in job_experience else 0
    candidate_years = sum([1 for exp in candidate_experience if "Intern" in exp["Role"]])
    return min(1, candidate_years / job_years) if job_years else 0.5

# Function to rank candidates for each job
def rank_candidates(jobs, candidates):
    results = []

    for job in jobs:
        job_title = job["JobTitle"]
        job_location = job["Location"]
        job_salary_range = job["Salary"]
        job_experience = job["Experience"]
        job_required_skills = job["RequiredSkills"]
        job_preferred_skills = job["PreferredSkills"]

        ranked_candidates = []

        for candidate_name, candidate in candidates.items():
            # Extract candidate skills
            candidate_skills = candidate["Technical Skills"]["Languages"] + \
                               candidate["Technical Skills"]["Frontend"] + \
                               candidate["Technical Skills"]["Backend"] + \
                               candidate["Technical Skills"]["Databases"] + \
                               candidate["Technical Skills"]["Operating Systems"]
            # Compute scores
            skills_score = compute_skills_score(job_required_skills + job_preferred_skills, candidate_skills)
            location_score = compute_location_score(job_location, candidate["Experience"][0]["Location"])
            salary_score = compute_salary_score(job_salary_range, candidate["Salary Desired"])
            experience_score = compute_experience_score(job_experience, candidate["Experience"])

            # Combine scores (weights can be adjusted)
            final_score = (0.3 * skills_score + 0.3 * location_score +
                           0.2 * salary_score + 0.2 * experience_score)

            ranked_candidates.append((candidate_name, final_score))

        ranked_candidates.sort(key=lambda x: x[1], reverse=True)
        results.append({"job": job_title, "candidates": ranked_candidates})

    return results

# Load data from JSON files
candidates_data = load_data('data/candidates.json')
employers_data = load_data('data/employers.json')

# Rank candidates for all jobs
ranked_results = rank_candidates(employers_data, candidates_data)

# Output the ranked candidates for each job
for job_result in ranked_results:
    print(f"Job Title: {job_result['job']}")
    print("Ranked Candidates:")
    for candidate_name, score in job_result["candidates"]:
        print(f"Candidate: {candidate_name}, Score: {score:.4f}")
    print("-" * 40)
