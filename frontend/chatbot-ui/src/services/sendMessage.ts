import { CHATBOT_API_URL } from "@/settings";

export function sendMessage(message: string, sessionId:string) {
  const options = { method: "POST", body: "false" };
  console.log(`${CHATBOT_API_URL}?chatInput=${message}`)
  return fetch(
    `${CHATBOT_API_URL}?chatInput=${message}&sessionId=${sessionId}`,
    options
  )
    .then((response) => {
        if(response.ok){
            return response.json()
            .then((data) => {return data.output})
        }else{
            throw new Error(`Error: ${response.status} ${response.statusText}`);
        }
    })
    .catch((err) => console.error(err));
}
