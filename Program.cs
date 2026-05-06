var data = File.ReadAllLines("data/br.csv");

Console.WriteLine(data.Length);
var minimum = 200.000;
var maximum = -1000.00;
var sum = 0.0;
var n = data.Length;

foreach (var line in data)
{
    var trimmed = line.TrimStart();
    if (trimmed.Length == 0 || trimmed[0] == '#')
        continue;

    var columns = line.Split(';', StringSplitOptions.TrimEntries);
    if (columns.Length < 2)
        continue;

    var city = columns[0];
    float value = float.Parse(columns[1]);

    if(value <= minimum)
        minimum = value;
    if(value >= maximum)
        maximum = value;
    
    sum = sum + value;

}

var avg = (sum/n);

Console.WriteLine($"minimum is {minimum}");
Console.WriteLine($"maximum is {maximum}");
Console.WriteLine($"avg is {avg}");

