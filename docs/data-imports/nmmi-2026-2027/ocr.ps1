param([Parameter(Mandatory=$true)][string]$RenderRoot,[string]$OutputRoot=$PSScriptRoot)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[Windows.Storage.StorageFile, Windows.Storage, ContentType=WindowsRuntime] | Out-Null
[Windows.Graphics.Imaging.BitmapDecoder, Windows.Foundation, ContentType=WindowsRuntime] | Out-Null
[Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType=WindowsRuntime] | Out-Null
$script:taskMethod=[System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and $_.IsGenericMethodDefinition -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' } | Select-Object -First 1
function Await-OcrOperation($Operation,[Type]$ResultType) {
 $task=$script:taskMethod.MakeGenericMethod($ResultType).Invoke($null,@($Operation))
 $task.GetAwaiter().GetResult()
}
$engine=[Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
foreach($number in 1..20){

 $img=Join-Path $RenderRoot ('page-{0:d3}.png' -f $number)
 $file=Await-OcrOperation ([Windows.Storage.StorageFile]::GetFileFromPathAsync($img)) ([Windows.Storage.StorageFile])
 $stream=Await-OcrOperation ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
 $decoder=Await-OcrOperation ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
 $bitmap=Await-OcrOperation ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
 $result=Await-OcrOperation ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
 $lines=@($result.Lines | ForEach-Object{
  $words=@($_.Words | ForEach-Object{ [ordered]@{text=$_.Text;x=$_.BoundingRect.X;y=$_.BoundingRect.Y;width=$_.BoundingRect.Width;height=$_.BoundingRect.Height} })
  $left=($words | ForEach-Object{$_.x}|Measure-Object -Minimum).Minimum
  $top=($words | ForEach-Object{$_.y}|Measure-Object -Minimum).Minimum
  [ordered]@{text=$_.Text;x=$left;y=$top;words=$words}
 })
 [ordered]@{pdf_page=$number;lines=$lines}|ConvertTo-Json -Depth 7|Set-Content -LiteralPath (Join-Path $OutputRoot ('ocr\page-{0:d3}.json' -f $number)) -Encoding UTF8
 $bitmap.Dispose();$stream.Dispose()
 if($number -eq 1 -or $number%5 -eq 0){Write-Output "OCR page $number"}
}