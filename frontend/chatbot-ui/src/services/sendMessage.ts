export function sendMessage(message: string) {
  const options = { method: "POST", body: "false" };
  return fetch(
    `http://localhost:5678/webhook/ask?chatInput=${message}`,
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
