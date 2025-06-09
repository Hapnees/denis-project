export const setUserData = () => {
  const user = localStorage.getItem('user')
  if (!user) return
  const parsedUser = JSON.parse(user)

  const email = parsedUser.email
  const userDataElement = document.getElementById('user-data')
  if (!userDataElement) return

  const userEmailElement = userDataElement.querySelector('p')
  if (!userEmailElement) return

  userEmailElement.textContent = email
}
