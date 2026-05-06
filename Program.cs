var data = File.ReadAllLines("data/weather_stations.csv");

Console.WriteLine(data.Length);

foreach (var line in data)
{
    var trimmed = line.TrimStart();
    if (trimmed.Length == 0 || trimmed[0] == '#')
        continue;

    var columns = line.Split(';', StringSplitOptions.TrimEntries);
    if (columns.Length < 2)
        continue;

    var city = columns[0];
    var temperature = columns[1];
    // Console.WriteLine($"{city};{temperature}");
}

