export function Select({ value, onValueChange, children }: {
  value: string,
  onValueChange: (value: string) => void,
  children: React.ReactNode
}) {
  return (
    <select
      value={value}
      onChange={(e) => onValueChange(e.target.value)}
      className="p-2 border rounded-md"
    >
      {children}
    </select>
  )
}

export function SelectItem({ value, children }: {
  value: string,
  children: React.ReactNode
}) {
  return <option value={value}>{children}</option>
}