document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-split-builder]").forEach((form) => {
    const daysContainer = form.querySelector("[data-days]");

    function refreshDayIndexes() {
      daysContainer.querySelectorAll("[data-day]").forEach((day, dayIndex) => {
        day.querySelectorAll("[data-day-index]").forEach((input) => {
          input.value = String(dayIndex);
        });
      });
    }

    function createExercise(dayIndex) {
      const row = document.createElement("div");
      row.className = "split-builder-exercise";
      row.dataset.exercise = "";
      row.innerHTML = `
        <input type="hidden" name="exercise_day_index[]" value="${dayIndex}" data-day-index>
        <label>
          Exercise
          <input type="text" name="exercise_name[]" required>
        </label>
        <label>
          Sets
          <input type="text" name="exercise_sets[]" value="3">
        </label>
        <label>
          Reps
          <input type="text" name="exercise_reps[]" value="8-12">
        </label>
        <label>
          Rest
          <input type="text" name="exercise_rest[]">
        </label>
        <button type="button" class="button secondary-button compact-button" data-remove-exercise>Remove</button>
      `;
      return row;
    }

    function createDay() {
      const dayIndex = daysContainer.querySelectorAll("[data-day]").length;
      const day = document.createElement("section");
      day.className = "split-builder-day";
      day.dataset.day = "";
      day.innerHTML = `
        <div class="split-builder-heading">
          <label>
            Workout Day
            <input type="text" name="day_name[]" value="Day ${dayIndex + 1}" required>
          </label>
          <label>
            Focus
            <input type="text" name="day_focus[]">
          </label>
          <button type="button" class="button secondary-button compact-button" data-remove-day>Remove Day</button>
        </div>
        <div class="split-builder-exercises" data-exercises></div>
        <button type="button" class="button secondary-button compact-button" data-add-exercise>Add Exercise</button>
      `;
      day.querySelector("[data-exercises]").append(createExercise(dayIndex));
      return day;
    }

    form.addEventListener("click", (event) => {
      const addDay = event.target.closest("[data-add-day]");
      const addExercise = event.target.closest("[data-add-exercise]");
      const removeDay = event.target.closest("[data-remove-day]");
      const removeExercise = event.target.closest("[data-remove-exercise]");

      if (addDay) {
        daysContainer.append(createDay());
        refreshDayIndexes();
      }

      if (addExercise) {
        const day = addExercise.closest("[data-day]");
        const dayIndex = Array.from(daysContainer.querySelectorAll("[data-day]")).indexOf(day);
        day.querySelector("[data-exercises]").append(createExercise(dayIndex));
        refreshDayIndexes();
      }

      if (removeDay) {
        const days = daysContainer.querySelectorAll("[data-day]");
        if (days.length > 1) {
          removeDay.closest("[data-day]").remove();
          refreshDayIndexes();
        }
      }

      if (removeExercise) {
        const exerciseList = removeExercise.closest("[data-exercises]");
        if (exerciseList.querySelectorAll("[data-exercise]").length > 1) {
          removeExercise.closest("[data-exercise]").remove();
          refreshDayIndexes();
        }
      }
    });

    refreshDayIndexes();
  });
});
