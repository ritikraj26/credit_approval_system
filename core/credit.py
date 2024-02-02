import openai
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY

def generate_credit_rating(past_loans_paid_on_time, number_of_loans_taken, loan_activity_in_current_year, loan_approved_volume):
    # text = "Generate a credit rating between 0 and 60 based on past loans paid on time, number of loans taken, loan activity in the current year, and loan approved volume."
    # prompt = f"{text}\n\nPast loans paid on time: {past_loans_paid_on_time}\nNumber of loans taken: {number_of_loans_taken}\nLoan activity in the current year: {loan_activity_in_current_year}\nLoan approved volume: {loan_approved_volume}\n\nCredit rating: "
    
    # response = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #     messages=[
    #         {"role": "system", "content": "You are a helpful assistant."},
    #         {"role": "user", "content": prompt},
    #     ],
    #     temperature=0.1,
    # )
    
    # return response['choices'][0]['message']['content']
    credit_rating = 15
    
    if number_of_loans_taken == 0:
        credit_rating += 15
    else:
        if number_of_loans_taken == past_loans_paid_on_time:
            credit_rating += 12
        else:
            credit_rating += 8
    
    if loan_activity_in_current_year == 0:
        credit_rating += 15
    else:
        credit_rating += 10

    if loan_approved_volume == 0:
        credit_rating += 15
    else:
        credit_rating += 10

    return credit_rating