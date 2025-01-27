
# Billboard Hot 100 Dataset

This dataset contains the complete historical record of every Billboard Hot 100 chart since 1958. The data is stored in a `hot_100.parquet` file, containing weekly Billboard 100 chart data from its inception until today.

## Data Dictionary

### `chart_position`
- **Description**: The position of the song on the chart for the given chart date.

### `chart_date`
- **Description**: The release date of the chart.

### `song`
- **Description**: The name of the song.

### `performer`
- **Description**: The performer or artist of the song.

### `song_id`
- **Description**: A unique identifier created by concatenating the `song` and `performer` fields.

### `instance`
- **Description**: Indicates how many times a `song_id` has returned to the chart after more than one week off the chart.  
  - *Example*: "Mariah Carey - All I Want for Christmas Is You" has multiple instances for its repeated appearances during holiday seasons.

### `time_on_chart`
- **Description**: The cumulative count of weeks (all-time) a `song_id` has been on the chart.

### `consecutive_weeks`
- **Description**: For a given instance, how many weeks the `song_id` has consecutively remained on the chart.  
  - *Note*: A `null` value indicates the start of a new instance.

### `previous_week`
- **Description**: For a given instance, the `chart_position` of the song in the previous week.

### `peak_position`
- **Description**: The all-time best (highest) position achieved by a `song_id` on the chart.

### `worst_position`
- **Description**: The all-time worst (lowest) position achieved by a `song_id` on the chart.

### `chart_debut`
- **Description**: The date of the first initial instance for a `song_id`.

### `chart_url`
- **Description**: A URL link to the corresponding chart on Billboard.com.

---

## Download Dataset
You can download the dataset directly [here](hot_100.parquet).
