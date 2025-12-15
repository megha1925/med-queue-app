export async function processReferral(referral: {referral_text:string, province:string}){
  const res = await fetch('/api/process_referral', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(referral)
  })
  return res.json()
}
