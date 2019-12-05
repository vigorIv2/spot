{{/* vim: set filetype=mustache: */}}

{{- define "nodes" -}}
{{- $nodeCount := .replicaCount | int }}
{{- $site := .siteName -}}
  {{- range $index0 := until $nodeCount -}}
    {{- $index1 := $index0 | add1 -}}
{{ $site }}-{{ $index0 }}.{{ $site }}{{ if ne $index1 $nodeCount }},{{ end }}
  {{- end -}}
{{- end -}}
