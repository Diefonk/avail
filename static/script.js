function setTimezone() {
	const date = new Date();
	const offset = date.getTimezoneOffset();
	const picker = document.getElementById("timezone");
	for (let index = 0; index < picker.length; index++) {
		if (picker.options[index].value == offset) {
			picker.selectedIndex = index;
			break;
		}
	}
}
