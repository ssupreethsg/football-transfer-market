import PlayerView from "./PlayerView";

export default async function PlayerPage({ params }: PageProps<"/players/[id]">) {
  const { id } = await params;
  return <PlayerView id={id} />;
}
